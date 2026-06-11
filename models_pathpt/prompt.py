"""models_pathpt/prompt.py — θ_t: prompt-tuning (CoOp) sobre el text encoder de CONCH.

Port de `PathPT_reference/models/PathPT_model_CONCH.py` (pin 0ab7f1b), clases
`CONCHTextEncoder` + `PromptLearnerCONCH`, **adaptado a nuestro CONCH**
(`conch.open_clip_custom`, en clam_environ/CONCH, READ-ONLY) en vez del fork
`open_clip_CONCH` de la referencia.

API verificada compatible (de-risk 10-jun): nuestro CoCa expone
`model.text.{transformer,positional_embedding,ln_final,text_projection,cls_emb,
attn_mask,heads,pad_id,output_tokens}` y `model._encode_text(ids) -> (pooled[*,512],
embedding[*,127,768])`. ctx_dim=768, espacio contrastivo de salida=512.

θ_t = `self.ctx` (n_cls, n_ctx=32, 768): vectores de contexto APRENDIBLES inyectados
entre [SOS] y [CLS+EOS] como token-embeddings; el text-transformer de CONCH corre
congelado sobre ellos (gradiente fluye solo a `ctx`). CONCH NO se entrena.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


def prompt_padding(ctx, length, mode="repeat"):
    """Repite las palabras del prompt-init hasta cubrir `length` tokens (ref verbatim)."""
    if mode == "repeat":
        words = ctx.split()
        repeat_times = (length + len(words) - 1) // len(words)
        padded_words = (words * repeat_times)[:length]
        return " ".join(padded_words)
    raise ValueError("Solo 'repeat' soportado.")


class CONCHTextEncoder(nn.Module):
    """Corre el text-transformer (CONGELADO) de CONCH desde token-embeddings.

    Recibe los embeddings de prompt (prefix+ctx+suffix) en vez de IDs, para que el
    gradiente retroceda hasta `ctx`. Port verbatim de la referencia (la API de
    model.text de nuestro CoCa coincide pieza por pieza)."""

    def __init__(self, model, embed_cls=True):
        super().__init__()
        text_model = model.text
        self.transformer = text_model.transformer
        self.positional_embedding = text_model.positional_embedding
        self.ln_final = text_model.ln_final
        self.text_projection = text_model.text_projection
        self.dtype = self.transformer.get_cast_dtype()
        self.embed_cls = embed_cls
        self.attn_mask = text_model.attn_mask
        self.heads = text_model.heads
        self.pad_id = text_model.pad_id
        self.output_tokens = text_model.output_tokens
        self.cls_emb = text_model.cls_emb if embed_cls else None

    def build_cls_mask(self, text_tokens, cast_dtype):
        cls_mask = (text_tokens != self.pad_id).unsqueeze(1)
        cls_mask = F.pad(cls_mask, (1, 0, cls_mask.shape[2], 0), value=1.0)
        additive_mask = torch.empty(cls_mask.shape, dtype=cast_dtype, device=cls_mask.device)
        additive_mask.fill_(0)
        additive_mask.masked_fill_(~cls_mask, float("-inf"))
        additive_mask = torch.repeat_interleave(additive_mask, self.heads, 0)
        return additive_mask

    def _repeat(self, t, N):
        return t.reshape(1, 1, -1).repeat(N, 1, 1)

    def forward(self, x, prompt_tokens):
        # x: token-embeddings del prompt [n_cls, seq, 768]; prompt_tokens: IDs [n_cls, 128]
        prompt_tokens = prompt_tokens[:, :-1] if self.embed_cls else prompt_tokens  # hueco para CLS
        cast_dtype = self.dtype
        seq_len = x.shape[1]
        x = x.to(cast_dtype)
        attn_mask = self.attn_mask
        if self.cls_emb is not None:
            seq_len += 1
            x = torch.cat([x, self._repeat(self.cls_emb, x.shape[0])], dim=1)
            cls_mask = self.build_cls_mask(prompt_tokens, cast_dtype).to(attn_mask.device)
            attn_mask = attn_mask[None, :seq_len, :seq_len] + cls_mask[:, :seq_len, :seq_len]

        x = x + self.positional_embedding[:seq_len].to(cast_dtype)
        x = x.permute(1, 0, 2)  # NLD -> LND
        x = self.transformer(x, attn_mask=attn_mask)
        x = x.permute(1, 0, 2)  # LND -> NLD

        if self.cls_emb is not None:
            pooled = self.ln_final(x[:, -1])
        else:
            x = self.ln_final(x)
            pooled = x[torch.arange(x.shape[0]), prompt_tokens.argmax(dim=-1)]

        if self.text_projection is not None:
            pooled = pooled @ self.text_projection
        return pooled  # [n_cls, 512] en el espacio contrastivo


class PromptLearnerCONCH(nn.Module):
    """CoOp: n_ctx vectores de contexto aprendibles (768) + clase fija.

    `classnames_lst`: lista de n_cls elementos; cada uno es una lista de strings de
    clase (variantes) — solo se usa la 1ª como init (la ref randomiza con
    change_classnames(); acá fijamos la 1ª para reproducibilidad)."""

    def __init__(self, classnames_lst, model, device, n_ctx=32,
                 ctx_init="a histopathology image of ", tokenizer=None):
        super().__init__()
        from conch.open_clip_custom import get_tokenizer, tokenize
        self.device = device
        self._tokenize = tokenize
        tokenizer = tokenizer or get_tokenizer()
        n_cls = len(classnames_lst)

        # init del contexto desde un prompt-template (mode 'template')
        ctx_init = prompt_padding(ctx_init, n_ctx)
        prompt = tokenize(tokenizer, [ctx_init] * n_cls)
        with torch.no_grad():
            _, embedding = model._encode_text(prompt.to(device))  # [n_cls, 127, 768]
        ctx_vectors = embedding[:, 1 : 1 + n_ctx, :].clone()      # [n_cls, n_ctx, 768]
        self.ctx = nn.Parameter(ctx_vectors)                       # ← APRENDIBLE (θ_t)

        # prefijo (SOS) + sufijo (CLS+EOS) por clase, desde la 1ª variante de cada clase
        embeddings, tok_lst = [], []
        for classnames in classnames_lst:
            cls_prompts = [" ".join(["X"] * n_ctx) + " " + name + "." for name in classnames]
            tok = tokenize(tokenizer, cls_prompts)               # [n_var, 128]
            tok_lst.append(tok)
            with torch.no_grad():
                _, emb = model._encode_text(tok.to(device))      # [n_var, 127, 768]
            embeddings.append(emb)

        init_embedding = torch.stack([e[0] for e in embeddings])  # [n_cls, 127, 768]
        tokenized_prompts = torch.stack([t[0] for t in tok_lst])  # [n_cls, 128]

        self.register_buffer("token_prefix", init_embedding[:, :1, :])         # SOS
        self.register_buffer("token_suffix", init_embedding[:, 1 + n_ctx :, :])  # CLS, EOS
        self.register_buffer("tokenized_prompts", tokenized_prompts)
        self.n_cls = n_cls
        self.n_ctx = n_ctx

    def forward(self):
        # reensambla [SOS | ctx aprendible | CLS+EOS] -> [n_cls, 127, 768]
        return torch.cat([self.token_prefix, self.ctx, self.token_suffix], dim=1)
