import numpy as np
import torch
from utils.utils import *
import os
from dataset_modules.dataset_generic import save_splits
from models.model_mil import MIL_fc, MIL_fc_mc
from models.model_clam import CLAM_SB, CLAM_MB, CLAM_WDM
from models.dtfd_mil import DTFD_MIL
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import auc as calc_auc

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Accuracy_Logger(object):
    """Accuracy logger"""
    def __init__(self, n_classes):
        super().__init__()
        self.n_classes = n_classes
        self.initialize()

    def initialize(self):
        self.data = [{"count": 0, "correct": 0} for i in range(self.n_classes)]

    def log(self, Y_hat, Y):
        Y_hat = int(Y_hat)
        Y = int(Y)
        self.data[Y]["count"] += 1
        self.data[Y]["correct"] += (Y_hat == Y)

    def log_batch(self, Y_hat, Y):
        Y_hat = np.array(Y_hat).astype(int)
        Y = np.array(Y).astype(int)
        for label_class in np.unique(Y):
            cls_mask = Y == label_class
            self.data[label_class]["count"] += cls_mask.sum()
            self.data[label_class]["correct"] += (Y_hat[cls_mask] == Y[cls_mask]).sum()

    def get_summary(self, c):
        count = self.data[c]["count"]
        correct = self.data[c]["correct"]

        if count == 0:
            acc = None
        else:
            acc = float(correct) / count

        return acc, correct, count


def get_flat_grads(model):
    grads = []

    for p in model.parameters():
        if not p.requires_grad:
            continue

        if p.grad is None:
            grads.append(torch.zeros_like(p).detach().view(-1))
        else:
            grads.append(p.grad.detach().clone().view(-1))

    if len(grads) == 0:
        return None

    return torch.cat(grads)


def grad_cosine(g1, g2, eps=1e-12):
    if g1 is None or g2 is None:
        return float("nan")

    denom = (torch.norm(g1) * torch.norm(g2)).clamp_min(eps)
    return (torch.dot(g1, g2) / denom).item()


def grad_dot(g1, g2):
    if g1 is None or g2 is None:
        return float("nan")

    return torch.dot(g1, g2).item()


def grad_norm(g):
    if g is None:
        return float("nan")

    return torch.norm(g).item()


def compute_class_weights_from_split(split_dataset, n_classes, device):
    labels = split_dataset.slide_data['label'].values
    counts = np.bincount(labels, minlength=n_classes).astype(np.float32)

    counts[counts == 0] = 1.0

    total = counts.sum()
    weights = np.sqrt(total / (n_classes * counts))

    weights = weights / weights.mean()

    weights = torch.tensor(weights, dtype=torch.float32, device=device)
    return weights


def get_slide_id_from_loader(loader, batch_idx):
    """
    Recupera el slide_id desde loader.dataset.slide_data.
    Funciona correctamente en validación/test si el loader no mezcla el orden.
    """
    if hasattr(loader.dataset, "slide_data"):
        if "slide_id" in loader.dataset.slide_data.columns:
            return loader.dataset.slide_data["slide_id"].iloc[batch_idx]

    return "unknown_slide_{}".format(batch_idx)


def build_probability_record(epoch, split, fold, batch_idx, slide_id, label, Y_hat, Y_prob, n_classes):
    """
    Construye una fila de logging con probabilidades por clase para una slide.
    """
    probs = Y_prob.detach().cpu().numpy().reshape(-1)

    true_label = int(label.item())
    pred_label = int(Y_hat.item())

    record = {
        "epoch": int(epoch) if epoch is not None else -1,
        "split": split,
        "fold": int(fold) if fold is not None else -1,
        "batch_idx": int(batch_idx),
        "slide_id": slide_id,
        "true_label": true_label,
        "pred_label": pred_label,
        "correct": int(true_label == pred_label),
        "prob_true_class": float(probs[true_label]),
        "max_probability": float(np.max(probs)),
    }

    for class_idx in range(n_classes):
        record["prob_class_{}".format(class_idx)] = float(probs[class_idx])

    return record


def save_probability_records(records, results_dir, filename):
    """
    Guarda registros de probabilidades en CSV.
    Si el archivo ya existe, agrega las nuevas filas.
    """
    if records is None or len(records) == 0:
        return

    import pandas as pd

    prob_dir = os.path.join(results_dir, "probability_logs")
    os.makedirs(prob_dir, exist_ok=True)

    save_path = os.path.join(prob_dir, filename)

    new_df = pd.DataFrame(records)

    if os.path.exists(save_path):
        old_df = pd.read_csv(save_path)
        new_df = pd.concat([old_df, new_df], ignore_index=True)

    new_df.to_csv(save_path, index=False)
    print("Saved probability log:", save_path)


class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience.
    Además guarda checkpoints por:
    - menor val_loss
    - menor val_error
    - mayor val_auc
    """

    def __init__(self, patience=20, stop_epoch=50, verbose=False):
        self.patience = patience
        self.stop_epoch = stop_epoch
        self.verbose = verbose

        self.counter = 0
        self.best_score = None
        self.early_stop = False

        self.val_loss_min = np.inf
        self.val_error_min = np.inf
        self.val_auc_max = -np.inf

    def __call__(
        self,
        epoch,
        val_loss,
        model,
        ckpt_name='checkpoint.pt',
        val_error=None,
        val_auc=None,
        ckpt_name_error=None,
        ckpt_name_auc=None
    ):
# DESPUÉS — usa AUC como criterio principal si está disponible:
        # Usa AUC si está disponible, si no cae a val_loss
        if val_auc is not None:
            score = val_auc          # maximizar AUC
        else:
            score = -val_loss        # minimizar loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint_loss(val_loss, model, ckpt_name)
        elif score <= self.best_score:
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience and epoch > self.stop_epoch:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint_loss(val_loss, model, ckpt_name)
            self.counter = 0

        # Nuevo criterio: menor val_error
        if val_error is not None and ckpt_name_error is not None:
            if val_error < self.val_error_min:
                if self.verbose:
                    print(
                        f'Validation error decreased '
                        f'({self.val_error_min:.6f} --> {val_error:.6f}). '
                        f'Saving best-val-error model ...'
                    )
                torch.save(model.state_dict(), ckpt_name_error)
                self.val_error_min = val_error

        # Nuevo criterio: mayor val_auc
        if val_auc is not None and ckpt_name_auc is not None:
            if val_auc > self.val_auc_max:
                if self.verbose:
                    print(
                        f'Validation AUC increased '
                        f'({self.val_auc_max:.6f} --> {val_auc:.6f}). '
                        f'Saving best-val-auc model ...'
                    )
                torch.save(model.state_dict(), ckpt_name_auc)
                self.val_auc_max = val_auc

    def save_checkpoint_loss(self, val_loss, model, ckpt_name):
        if self.verbose:
            print(
                f'Validation loss decreased '
                f'({self.val_loss_min:.6f} --> {val_loss:.6f}). '
                f'Saving model ...'
            )
        torch.save(model.state_dict(), ckpt_name)
        self.val_loss_min = val_loss


def train(datasets, cur, args):
    """
    train for a single fold
    """
    print('\nTraining Fold {}!'.format(cur))
    writer_dir = os.path.join(args.results_dir, str(cur))
    if not os.path.isdir(writer_dir):
        os.mkdir(writer_dir)

    if args.log_data:
        from tensorboardX import SummaryWriter
        writer = SummaryWriter(writer_dir, flush_secs=15)
    else:
        writer = None

    print('\nInit train/val/test splits...', end=' ')
    train_split, val_split, test_split = datasets
    save_splits(datasets, ['train', 'val', 'test'], os.path.join(args.results_dir, 'splits_{}.csv'.format(cur)))
    print('Done!')
    print("Training on {} samples".format(len(train_split)))
    print("Validating on {} samples".format(len(val_split)))
    print("Testing on {} samples".format(len(test_split)))

    print('\nInit loss function...', end=' ')
    class_weights = None
    if hasattr(args, 'auto_class_weights') and args.auto_class_weights:
        class_weights = compute_class_weights_from_split(
            train_split,
            n_classes=args.n_classes,
            device=device
        )
        print("Auto class weights:", class_weights.detach().cpu().numpy())

    # Override manual del peso de la clase positiva (campaña papilar).
    # Solo binario + CE. Tiene prioridad sobre auto_class_weights.
    cw_pos = getattr(args, 'class_weight_pos', None)
    if cw_pos is not None and args.n_classes == 2 and args.bag_loss == 'ce':
        class_weights = torch.tensor([1.0, float(cw_pos)], dtype=torch.float32, device=device)
        print("Manual class weights [neg, pos]:", class_weights.detach().cpu().numpy())

    if args.bag_loss == 'svm':
        from topk.svm import SmoothTop1SVM
        loss_fn = SmoothTop1SVM(n_classes=args.n_classes)
        if device.type == 'cuda':
            loss_fn = loss_fn.cuda()
    else:
        loss_fn = nn.CrossEntropyLoss(weight=class_weights)
    print('Done!')

    print('\nInit Model...', end=' ')
    model_dict = {
        "dropout": args.drop_out,
        "n_classes": args.n_classes,
        "embed_dim": args.embed_dim
    }

    if hasattr(args, "use_mammoth"):
        model_dict.update({
            "use_mammoth": args.use_mammoth,
            "mammoth_num_experts": args.mammoth_num_experts,
            "mammoth_num_slots": args.mammoth_num_slots,
            "mammoth_num_heads": args.mammoth_num_heads,
            "mammoth_slot_dim": args.mammoth_slot_dim,
        })

    if args.model_size is not None and args.model_type != 'mil':
        model_dict.update({"size_arg": args.model_size})

    if args.model_type in ["clam_sb", "clam_mb"]:
        model_dict.update({
            "use_mammoth": getattr(args, "use_mammoth", False),
            "mammoth_num_experts": getattr(args, "mammoth_num_experts", 8),
            "mammoth_num_slots": getattr(args, "mammoth_num_slots", 4),
            "mammoth_num_heads": getattr(args, "mammoth_num_heads", 8),
            "mammoth_slot_dim": getattr(args, "mammoth_slot_dim", 256),
        })

    if args.model_type in ['clam_sb', 'clam_mb', 'clam_wdm']:
        if args.subtyping:
            model_dict.update({'subtyping': True})

        if args.B > 0:
            model_dict.update({'k_sample': args.B})

        if args.inst_loss == 'svm':
            from topk.svm import SmoothTop1SVM
            instance_loss_fn = SmoothTop1SVM(n_classes=2)
            if device.type == 'cuda':
                instance_loss_fn = instance_loss_fn.cuda()
        else:
            instance_loss_fn = nn.CrossEntropyLoss()

        if args.model_type == 'clam_sb':
            model = CLAM_SB(**model_dict, instance_loss_fn=instance_loss_fn)
        elif args.model_type == 'clam_mb':
            model = CLAM_MB(**model_dict, instance_loss_fn=instance_loss_fn)
        elif args.model_type == 'clam_wdm':
            model = CLAM_WDM(
                gate=True,
                size_arg=args.model_size,
                dropout=args.drop_out,
                k_sample=args.B,
                n_classes=args.n_classes,
                instance_loss_fn=instance_loss_fn,
                subtyping=args.subtyping,
                embed_dim=args.embed_dim,
                use_channel_mixer=True
            )
        else:
            raise NotImplementedError

    elif args.model_type == 'dtfd_mil':
        dtfd_dict = {
            "embed_dim":           args.embed_dim,
            "n_classes":           args.n_classes,
            "dropout":             args.drop_out,
            "size_arg":            getattr(args, "model_size", "small") or "small",
            "num_pseudo_bags":     getattr(args, "num_pseudo_bags", 8),
            "pseudo_bag_size":     getattr(args, "pseudo_bag_size", None),
            "distill_temperature": getattr(args, "distill_temperature", 3.0),
            "distill_weight":      getattr(args, "distill_weight", 0.5),
            "use_mammoth":         getattr(args, "use_mammoth", False),
            "mammoth_num_experts": getattr(args, "mammoth_num_experts", 30),
            "mammoth_num_slots":   getattr(args, "mammoth_num_slots", 10),
            "mammoth_num_heads":   getattr(args, "mammoth_num_heads", 16),
            "mammoth_slot_dim":    getattr(args, "mammoth_slot_dim", 256),
        }
        model = DTFD_MIL(**dtfd_dict)

    else:
        if args.n_classes > 2:
            model = MIL_fc_mc(**model_dict)
        else:
            model = MIL_fc(**model_dict)

    _ = model.to(device)
    print('Done!')
    print_network(model)

    print('\nInit optimizer ...', end=' ')
    optimizer = get_optim(model, args)
    print('Done!')

    # LR scheduler opcional (campaña papilar). 'plateau' usa val_loss; 'cosine' avanza por epoch.
    scheduler_name = getattr(args, 'scheduler', 'none')
    base_opt = optimizer.optimizer if hasattr(optimizer, 'optimizer') else optimizer
    if scheduler_name == 'plateau':
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            base_opt, mode='min', factor=0.5, patience=8, min_lr=1e-6
        )
        print('LR scheduler: ReduceLROnPlateau(factor=0.5, patience=8)')
    elif scheduler_name == 'cosine':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            base_opt, T_max=args.max_epochs, eta_min=1e-6
        )
        print('LR scheduler: CosineAnnealingLR(T_max={})'.format(args.max_epochs))
    else:
        scheduler = None

    print('\nInit Loaders...', end=' ')
    train_loader = get_split_loader(train_split, training=True, testing=args.testing, weighted=args.weighted_sample)
    val_loader = get_split_loader(val_split, testing=args.testing)
    test_loader = get_split_loader(test_split, testing=args.testing)
    print('Done!')

    print('\nSetup EarlyStopping...', end=' ')
    if args.early_stopping:
        early_stopping = EarlyStopping(patience=20, stop_epoch=15, verbose=True)
    else:
        early_stopping = None
    print('Done!')

    for epoch in range(args.max_epochs):
        if args.model_type in ['clam_sb', 'clam_mb', 'clam_wdm', 'dtfd_mil'] and not args.no_inst_cluster:
            train_loop_clam(
                epoch, model, train_loader, optimizer,
                args.n_classes, args.bag_weight,
                writer, loss_fn, args
            )

            stop, val_loss = validate_clam(
                cur, epoch, model, val_loader, args.n_classes,
                early_stopping, writer, loss_fn, args.results_dir
            )
        else:
            train_loop(epoch, model, train_loader, optimizer, args.n_classes, writer, loss_fn)

            stop, val_loss = validate(
                cur, epoch, model, val_loader, args.n_classes,
                early_stopping, writer, loss_fn, args.results_dir
            )

        # Avanza el LR scheduler (plateau usa val_loss; cosine avanza por epoch).
        if scheduler is not None:
            if scheduler_name == 'plateau':
                scheduler.step(val_loss)
            else:
                scheduler.step()
            if writer:
                writer.add_scalar('train/lr', base_opt.param_groups[0]['lr'], epoch)

        if stop:
            break

# DESPUÉS — carga el mejor por AUC si existe:
    if args.early_stopping:
        ckpt_auc_path = os.path.join(args.results_dir, "s_{}_checkpoint_best_auc.pt".format(cur))
        ckpt_loss_path = os.path.join(args.results_dir, "s_{}_checkpoint.pt".format(cur))
        load_path = ckpt_auc_path if os.path.exists(ckpt_auc_path) else ckpt_loss_path
        model.load_state_dict(torch.load(load_path))
        print(f"Loaded checkpoint from: {load_path}")
    else:
        torch.save(model.state_dict(), os.path.join(args.results_dir, "s_{}_checkpoint.pt".format(cur)))

    _, val_error, val_auc, _ = summary(
        model,
        val_loader,
        args.n_classes,
        split="val_final",
        fold=cur,
        results_dir=args.results_dir
    )
    print('Val error: {:.4f}, ROC AUC: {:.4f}'.format(val_error, val_auc))

    results_dict, test_error, test_auc, acc_logger = summary(
        model,
        test_loader,
        args.n_classes,
        split="test",
        fold=cur,
        results_dir=args.results_dir
    )
    print('Test error: {:.4f}, ROC AUC: {:.4f}'.format(test_error, test_auc))

    for i in range(args.n_classes):
        acc, correct, count = acc_logger.get_summary(i)
        print('class {}: acc {}, correct {}/{}'.format(i, acc, correct, count))

        if writer:
            writer.add_scalar('final/test_class_{}_acc'.format(i), acc, 0)

    if writer:
        writer.add_scalar('final/val_error', val_error, 0)
        writer.add_scalar('final/val_auc', val_auc, 0)
        writer.add_scalar('final/test_error', test_error, 0)
        writer.add_scalar('final/test_auc', test_auc, 0)
        writer.close()

    return results_dict, test_auc, val_auc, 1 - test_error, 1 - val_error


def train_loop_clam(epoch, model, loader, optimizer, n_classes, bag_weight, writer=None, loss_fn=None, args=None):
    model.train()
    acc_logger = Accuracy_Logger(n_classes=n_classes)
    inst_logger = Accuracy_Logger(n_classes=n_classes)

    train_loss = 0.
    train_error = 0.
    train_inst_loss = 0.
    inst_count = 0
    gradient_rows = []

    print('\n')
    for batch_idx, batch in enumerate(loader):
        if batch is None:
            continue

        data, label = batch
        data = data.to(device)
        label = label.to(device)

        logits, Y_prob, Y_hat, _, instance_dict = model(data, label=label, instance_eval=True)

        acc_logger.log(Y_hat, label)
        loss = loss_fn(logits, label)
        loss_value = loss.item()

        instance_loss = instance_dict['instance_loss']
        inst_count += 1
        instance_loss_value = instance_loss.item()
        train_inst_loss += instance_loss_value

        total_loss = bag_weight * loss + (1 - bag_weight) * instance_loss

        if getattr(args, "confidence_penalty", 0.0) > 0:
            confidence_penalty = torch.sum(Y_prob * torch.log(Y_prob + 1e-8), dim=1).mean()
            total_loss = total_loss + args.confidence_penalty * confidence_penalty
        else:
            confidence_penalty = torch.tensor(0.0, device=total_loss.device)

        losses = [
            bag_weight * loss,
            (1 - bag_weight) * instance_loss
        ]

        inst_preds = instance_dict['inst_preds']
        inst_labels = instance_dict['inst_labels']
        inst_logger.log_batch(inst_preds, inst_labels)

        train_loss += loss_value

        if (batch_idx + 1) % 20 == 0:
            print(
                'batch {}, loss: {:.4f}, instance_loss: {:.4f}, weighted_loss: {:.4f}, '.format(
                    batch_idx, loss_value, instance_loss_value, total_loss.item()
                ) +
                'label: {}, bag_size: {}'.format(label.item(), data.size(0))
            )

        error = calculate_error(Y_hat, label)
        train_error += error

        log_gradients = getattr(args, "log_gradients", False)

        if log_gradients:
            optimizer.zero_grad()
            losses[0].backward(retain_graph=True)
            g_slide = get_flat_grads(model)

            optimizer.zero_grad()
            losses[1].backward(retain_graph=True)
            g_inst = get_flat_grads(model)

            cos_slide_inst = grad_cosine(g_slide, g_inst)
            dot_slide_inst = grad_dot(g_slide, g_inst)

            gradient_rows.append({
                "epoch": epoch,
                "batch_idx": batch_idx,
                "label": int(label.item()),
                "loss_slide": float(loss.item()),
                "loss_instance": float(instance_loss.item()),
                "loss_total": float(total_loss.item()),
                "cos_slide_inst": cos_slide_inst,
                "dot_slide_inst": dot_slide_inst,
                "grad_norm_slide": grad_norm(g_slide),
                "grad_norm_inst": grad_norm(g_inst),
                "pcgrad_enabled": bool(getattr(args, "pcgrad", False)),
                "confidence_penalty": float(confidence_penalty.item()),
            })

            optimizer.zero_grad()

        if getattr(args, "pcgrad", False):
            optimizer.pc_backward(losses, model)
        else:
            total_loss.backward()

        if log_gradients:
            g_total = get_flat_grads(model)
            gradient_rows[-1]["grad_norm_total"] = grad_norm(g_total)

        optimizer.step()
        optimizer.zero_grad()

    train_loss /= len(loader)
    train_error /= len(loader)

    if inst_count > 0:
        train_inst_loss /= inst_count
        print('\n')
        for i in range(2):
            acc, correct, count = inst_logger.get_summary(i)
            print('class {} clustering acc {}: correct {}/{}'.format(i, acc, correct, count))

    print(
        'Epoch: {}, train_loss: {:.4f}, train_clustering_loss:  {:.4f}, train_error: {:.4f}'.format(
            epoch, train_loss, train_inst_loss, train_error
        )
    )

    for i in range(n_classes):
        acc, correct, count = acc_logger.get_summary(i)
        print('class {}: acc {}, correct {}/{}'.format(i, acc, correct, count))

        if writer and acc is not None:
            writer.add_scalar('train/class_{}_acc'.format(i), acc, epoch)

    if writer:
        writer.add_scalar('train/loss', train_loss, epoch)
        writer.add_scalar('train/error', train_error, epoch)
        writer.add_scalar('train/clustering_loss', train_inst_loss, epoch)

    if getattr(args, "log_gradients", False) and len(gradient_rows) > 0:
        import pandas as pd

        grad_dir = os.path.join(args.results_dir, "gradient_logs")
        os.makedirs(grad_dir, exist_ok=True)

        grad_path = os.path.join(grad_dir, "gradients_epoch_{}.csv".format(epoch))
        pd.DataFrame(gradient_rows).to_csv(grad_path, index=False)

        print("Saved gradient log:", grad_path)


def train_loop(epoch, model, loader, optimizer, n_classes, writer=None, loss_fn=None):
    model.train()
    acc_logger = Accuracy_Logger(n_classes=n_classes)
    train_loss = 0.
    train_error = 0.

    print('\n')
    for batch_idx, batch in enumerate(loader):
        if batch is None:
            continue

        data, label = batch
        data = data.to(device)
        label = label.to(device)

        logits, Y_prob, Y_hat, _, instance_dict = model(data, label=label, instance_eval=True)

        acc_logger.log(Y_hat, label)
        loss = loss_fn(logits, label)
        loss_value = loss.item()

        train_loss += loss_value

        if (batch_idx + 1) % 20 == 0:
            print(
                'batch {}, loss: {:.4f}, label: {}, bag_size: {}'.format(
                    batch_idx, loss_value, label.item(), data.size(0)
                )
            )

        error = calculate_error(Y_hat, label)
        train_error += error

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    train_loss /= len(loader)
    train_error /= len(loader)

    print('Epoch: {}, train_loss: {:.4f}, train_error: {:.4f}'.format(epoch, train_loss, train_error))

    for i in range(n_classes):
        acc, correct, count = acc_logger.get_summary(i)
        print('class {}: acc {}, correct {}/{}'.format(i, acc, correct, count))

        if writer:
            writer.add_scalar('train/class_{}_acc'.format(i), acc, epoch)

    if writer:
        writer.add_scalar('train/loss', train_loss, epoch)
        writer.add_scalar('train/error', train_error, epoch)


def validate(cur, epoch, model, loader, n_classes, early_stopping=None, writer=None, loss_fn=None, results_dir=None):
    model.eval()
    acc_logger = Accuracy_Logger(n_classes=n_classes)

    val_loss = 0.
    val_error = 0.

    prob = np.zeros((len(loader), n_classes))
    labels = np.zeros(len(loader))

    probability_records = []

    with torch.no_grad():
        for batch_idx, (data, label) in enumerate(loader):
            data = data.to(device, non_blocking=True)
            label = label.to(device, non_blocking=True)

            logits, Y_prob, Y_hat, _, _ = model(data)

            acc_logger.log(Y_hat, label)

            loss = loss_fn(logits, label)

            prob[batch_idx] = Y_prob.cpu().numpy()
            labels[batch_idx] = label.item()

            slide_id = get_slide_id_from_loader(loader, batch_idx)

            probability_records.append(
                build_probability_record(
                    epoch=epoch,
                    split="val",
                    fold=cur,
                    batch_idx=batch_idx,
                    slide_id=slide_id,
                    label=label,
                    Y_hat=Y_hat,
                    Y_prob=Y_prob,
                    n_classes=n_classes
                )
            )

            val_loss += loss.item()
            error = calculate_error(Y_hat, label)
            val_error += error

    val_error /= len(loader)
    val_loss /= len(loader)

    if n_classes == 2:
        auc = roc_auc_score(labels, prob[:, 1])
    else:
        auc = roc_auc_score(labels, prob, multi_class='ovr')

    if writer:
        writer.add_scalar('val/loss', val_loss, epoch)
        writer.add_scalar('val/auc', auc, epoch)
        writer.add_scalar('val/error', val_error, epoch)

    print('\nVal Set, val_loss: {:.4f}, val_error: {:.4f}, auc: {:.4f}'.format(val_loss, val_error, auc))

    for i in range(n_classes):
        acc, correct, count = acc_logger.get_summary(i)
        print('class {}: acc {}, correct {}/{}'.format(i, acc, correct, count))

    if results_dir is not None:
        save_probability_records(
            records=probability_records,
            results_dir=results_dir,
            filename="val_slide_probabilities_fold_{}.csv".format(cur)
        )

    if early_stopping:
        assert results_dir
        early_stopping(epoch, val_loss, model, ckpt_name=os.path.join(results_dir, "s_{}_checkpoint.pt".format(cur)))

        if early_stopping.early_stop:
            print("Early stopping")
            return True, val_loss

    return False, val_loss


def validate_clam(cur, epoch, model, loader, n_classes, early_stopping=None, writer=None, loss_fn=None, results_dir=None):
    model.eval()
    acc_logger = Accuracy_Logger(n_classes=n_classes)
    inst_logger = Accuracy_Logger(n_classes=n_classes)

    val_loss = 0.
    val_error = 0.

    val_inst_loss = 0.
    val_inst_acc = 0.
    inst_count = 0

    prob = np.zeros((len(loader), n_classes))
    labels = np.zeros(len(loader))

    probability_records = []

    sample_size = model.k_sample

    with torch.inference_mode():
        for batch_idx, batch in enumerate(loader):
            if batch is None:
                continue

            data, label = batch
            data = data.to(device)
            label = label.to(device)

            logits, Y_prob, Y_hat, _, instance_dict = model(data, label=label, instance_eval=True)

            acc_logger.log(Y_hat, label)

            loss = loss_fn(logits, label)

            val_loss += loss.item()

            instance_loss = instance_dict['instance_loss']

            inst_count += 1
            instance_loss_value = instance_loss.item()
            val_inst_loss += instance_loss_value

            inst_preds = instance_dict['inst_preds']
            inst_labels = instance_dict['inst_labels']
            inst_logger.log_batch(inst_preds, inst_labels)

            prob[batch_idx] = Y_prob.cpu().numpy()
            labels[batch_idx] = label.item()

            slide_id = get_slide_id_from_loader(loader, batch_idx)

            probability_records.append(
                build_probability_record(
                    epoch=epoch,
                    split="val",
                    fold=cur,
                    batch_idx=batch_idx,
                    slide_id=slide_id,
                    label=label,
                    Y_hat=Y_hat,
                    Y_prob=Y_prob,
                    n_classes=n_classes
                )
            )

            error = calculate_error(Y_hat, label)
            val_error += error

    val_error /= len(loader)
    val_loss /= len(loader)

    if n_classes == 2:
        auc = roc_auc_score(labels, prob[:, 1])
        aucs = []
    else:
        aucs = []
        binary_labels = label_binarize(labels, classes=[i for i in range(n_classes)])

        for class_idx in range(n_classes):
            if class_idx in labels:
                fpr, tpr, _ = roc_curve(binary_labels[:, class_idx], prob[:, class_idx])
                aucs.append(calc_auc(fpr, tpr))
            else:
                aucs.append(float('nan'))

        auc = np.nanmean(np.array(aucs))

    print('\nVal Set, val_loss: {:.4f}, val_error: {:.4f}, auc: {:.4f}'.format(val_loss, val_error, auc))

    if inst_count > 0:
        val_inst_loss /= inst_count
        for i in range(2):
            acc, correct, count = inst_logger.get_summary(i)
            print('class {} clustering acc {}: correct {}/{}'.format(i, acc, correct, count))

    if writer:
        writer.add_scalar('val/loss', val_loss, epoch)
        writer.add_scalar('val/auc', auc, epoch)
        writer.add_scalar('val/error', val_error, epoch)
        writer.add_scalar('val/inst_loss', val_inst_loss, epoch)

    for i in range(n_classes):
        acc, correct, count = acc_logger.get_summary(i)
        print('class {}: acc {}, correct {}/{}'.format(i, acc, correct, count))

        if writer and acc is not None:
            writer.add_scalar('val/class_{}_acc'.format(i), acc, epoch)

    if results_dir is not None:
        save_probability_records(
            records=probability_records,
            results_dir=results_dir,
            filename="val_slide_probabilities_fold_{}.csv".format(cur)
        )

# DESPUÉS:
    if early_stopping:
        assert results_dir
        early_stopping(
            epoch,
            val_loss,
            model,
            ckpt_name=os.path.join(results_dir, "s_{}_checkpoint.pt".format(cur)),
            val_error=val_error,
            val_auc=auc,
            ckpt_name_error=os.path.join(results_dir, "s_{}_checkpoint_best_error.pt".format(cur)),
            ckpt_name_auc=os.path.join(results_dir, "s_{}_checkpoint_best_auc.pt".format(cur)),
        )

        if early_stopping.early_stop:
            print("Early stopping")
            return True, val_loss

    return False, val_loss


def summary(model, loader, n_classes, split="test", fold=None, results_dir=None):
    acc_logger = Accuracy_Logger(n_classes=n_classes)
    model.eval()

    test_loss = 0.
    test_error = 0.

    all_probs = np.zeros((len(loader), n_classes))
    all_labels = np.zeros(len(loader))

    slide_ids = loader.dataset.slide_data['slide_id']
    patient_results = {}

    probability_records = []

    for batch_idx, batch in enumerate(loader):
        if batch is None:
            continue

        data, label = batch
        data = data.to(device)
        label = label.to(device)

        slide_id = slide_ids.iloc[batch_idx]

        with torch.inference_mode():
            logits, Y_prob, Y_hat, _, _ = model(data)

        acc_logger.log(Y_hat, label)

        probs = Y_prob.cpu().numpy()
        all_probs[batch_idx] = probs
        all_labels[batch_idx] = label.item()

        patient_results.update({
            slide_id: {
                'slide_id': np.array(slide_id),
                'prob': probs,
                'label': label.item()
            }
        })

        probability_records.append(
            build_probability_record(
                epoch=-1,
                split=split,
                fold=fold,
                batch_idx=batch_idx,
                slide_id=slide_id,
                label=label,
                Y_hat=Y_hat,
                Y_prob=Y_prob,
                n_classes=n_classes
            )
        )

        error = calculate_error(Y_hat, label)
        test_error += error

    test_error /= len(loader)

    if n_classes == 2:
        auc = roc_auc_score(all_labels, all_probs[:, 1])
        aucs = []
    else:
        aucs = []
        binary_labels = label_binarize(all_labels, classes=[i for i in range(n_classes)])

        for class_idx in range(n_classes):
            if class_idx in all_labels:
                fpr, tpr, _ = roc_curve(binary_labels[:, class_idx], all_probs[:, class_idx])
                aucs.append(calc_auc(fpr, tpr))
            else:
                aucs.append(float('nan'))

        auc = np.nanmean(np.array(aucs))

    if results_dir is not None:
        save_probability_records(
            records=probability_records,
            results_dir=results_dir,
            filename="final_{}_slide_probabilities_fold_{}.csv".format(split, fold)
        )

    return patient_results, test_error, auc, acc_logger