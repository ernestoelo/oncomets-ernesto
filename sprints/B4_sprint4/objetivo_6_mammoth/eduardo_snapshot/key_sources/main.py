from __future__ import print_function

import argparse
import pdb
import os
import math

# internal imports
from utils.file_utils import save_pkl, load_pkl
from utils.utils import *
from utils.core_utils import train
from dataset_modules.dataset_generic import Generic_WSI_Classification_Dataset, Generic_MIL_Dataset

# pytorch imports
import torch
from torch.utils.data import DataLoader, sampler
import torch.nn as nn
import torch.nn.functional as F

import pandas as pd
import numpy as np

########################################################
# TASK CONFIGURATION
########################################################

TASK_CONFIGS = {
    'task_1_tumor_vs_normal': {
        'csv_path': 'dataset_csv/tumor_vs_normal_dummy_clean.csv',
        'data_dir': 'tumor_vs_normal_resnet_features',  #! relative to args.data_root_dir
        'label_dict': {
            'normal_tissue': 0,
            'tumor_tissue': 1
        },
    },

    'task_2_tumor_subtyping': {
        'csv_path': 'dataset_csv/tumor_subtyping_dummy_clean.csv',
        'data_dir': 'tumor_subtyping_resnet_features',
        'label_dict': {
            'subtype_1': 0,
            'subtype_2': 1,
            'subtype_3': 2
        },
    },

    'tipo_histologico': {
        'csv_path': 'environ/csv_privado/dataset_tipo_histologico_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'carcinoma invasivo no residual': 1,
            'carcinoma invasivo de tipo no especifico (ductal)': 2,
            'carcinoma microinvasivo': 3,
            'carcinoma lobulillar invasivo':4,
            'carcinoma invasivo con caracteristicas mixtas ductales y lobulillares':5,
            'carcinoma tubular':6,
            'carcinoma cribiforme invasivo':7,
            'carcinoma mucinoso':8,
            'carcinoma micropapilar invasivo':9,
            'adenocarcinoma apocrino':10,
            'carcinoma metaplasico':11,
            'carcinoma papilar encapsulado con invasion':12,
            'carcinoma papilar solido con invasion':13,
            'adenocarcinoma papilar intraductal con invasion':14,
            'carcinoma adenoide quistico':15,
            'tumor neuroendocrino':16,
            'carcinoma neuroendocrino':17,
            },
    },
    
    'grado_histologico_aplica': {
        'csv_path': 'environ/csv_privado/dataset_grado_histologico_aplicable_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'si': 0,
            'no': 1,
            },
    },
    
    'grado_histologico_diferenciacion_tubular': {
        'csv_path': 'environ/csv_privado/dataset_grado_histologico_diferenciacion_tubular_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'score 1': 1,
            'score 2': 2,
            'score 3': 3
        }
    },
    
    'grado_histologico_pleomorfismo_nuclear': {
        'csv_path': 'environ/csv_privado/dataset_grado_histologico_pleomorfismo_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'score 1': 1,
            'score 2': 2,
            'score 3': 3
        }
    },
    
    'grado_histologico_mitotic_rate': {
        'csv_path': 'environ/csv_privado/dataset_grado_histologico_tasa_mitotica_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'score 1': 1,
            'score 2': 2,
            'score 3': 3
        }
    },
    
    'grado_histologico_grado_general': {
        'csv_path': 'environ/csv_privado/dataset_grado_histologico_grado_general_label.csv',
        'data_dir': 'features',
        'label_dict': {'no identificado': 0, 'grado 1': 1, 'grado 2': 2, 'grado 3': 3},
    },

    'carcinoma_ductal_insitu_presente': {
        'csv_path': 'environ/csv_privado/dataset_carcinoma_ductal_in_situ_presente_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'si': 0,
            'no': 1,
        }
    },
    
    'carcinoma_ductal_insitu_patron_arquitectonico': {
        'csv_path': 'environ/csv_privado/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'comedocarcinoma': 1,
            'enfermedad de paget': 2,
            'cribiforme': 3,
            'micropapilar': 4,
            'papilar': 5,
            'solido': 6
        }
    },
    
    'carcinoma_ductal_insitu_grado_nuclear': {
        'csv_path': 'environ/csv_privado/dataset_carcinoma_ductal_in_situ_grado_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'grado 1': 1,
            'grado 2': 2,
            'grado 3': 3
        }
    },
    
    'carcinoma_ductal_insitu_necrosis': {
        'csv_path': 'environ/csv_privado/dataset_carcinoma_ductal_in_situ_necrosis_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'focal': 1,
            'central': 2
        }
    },
    
    'invasion_linfatica_vascular': {
        'csv_path': 'environ/csv_privado/dataset_invasion_linfovascular_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'presente': 1
        }
    },
    
    'microcalcificaciones': {
        'csv_path': 'environ/csv_privado/dataset_microcalcificaciones_label.csv',
        'data_dir': 'features',
        'label_dict': {
            'no identificado': 0,
            'presentes en dcis': 1,
            'presentes en carcinoma invasivo': 2,
            'presentes en tejido no neoplasico': 3
        }
    },

    # Combined (private + TCGA) tasks
    'tipo_histologico_combined': {
        'csv_path': 'environ/csv/dataset_tipo_histologico_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_aplica_combined': {
        'csv_path': 'environ/csv/dataset_grado_histologico_aplicable_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_presente_combined': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_presente_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_pleomorfismo_nuclear_combined': {
        'csv_path': 'environ/csv/dataset_grado_histologico_pleomorfismo_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_mitotic_rate_combined': {
        'csv_path': 'environ/csv/dataset_grado_histologico_tasa_mitotica_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_grado_general_combined': {
        'csv_path': 'environ/csv/dataset_grado_histologico_grado_general_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_patron_arquitectonico_combined': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_grado_nuclear_combined': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_grado_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_necrosis_combined': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_necrosis_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'invasion_linfatica_vascular_combined': {
        'csv_path': 'environ/csv/dataset_invasion_linfovascular_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_combined': {
        'csv_path': 'environ/csv/dataset_microcalcificaciones_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_diferenciacion_tubular_combined': {
        'csv_path': 'environ/csv/dataset_grado_histologico_diferenciacion_tubular_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },

    # Private + TCGA + HistAI (pth) — same csv/ as combined but splits include histai samples
    'tipo_histologico_pth': {
        'csv_path': 'environ/csv/dataset_tipo_histologico_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_aplica_pth': {
        'csv_path': 'environ/csv/dataset_grado_histologico_aplicable_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_presente_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_presente_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_pleomorfismo_nuclear_pth': {
        'csv_path': 'environ/csv/dataset_grado_histologico_pleomorfismo_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_mitotic_rate_pth': {
        'csv_path': 'environ/csv/dataset_grado_histologico_tasa_mitotica_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_grado_general_pth': {
        'csv_path': 'environ/csv/dataset_grado_histologico_grado_general_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_diferenciacion_tubular_pth': {
        'csv_path': 'environ/csv/dataset_grado_histologico_diferenciacion_tubular_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_patron_arquitectonico_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_grado_nuclear_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_grado_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_necrosis_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_necrosis_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'invasion_linfatica_vascular_pth': {
        'csv_path': 'environ/csv/dataset_invasion_linfovascular_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_pth': {
        'csv_path': 'environ/csv/dataset_microcalcificaciones_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_en_carcinoma_invasivo_pth': {
        'csv_path': 'environ/csv/dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_en_cdis_pth': {
        'csv_path': 'environ/csv/dataset_microcalcificaciones_en_cdis_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_en_tejido_no_neoplasico_pth': {
        'csv_path': 'environ/csv/dataset_microcalcificaciones_en_tejido_no_neoplasico_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_cribiforme_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_cribiforme_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_micropapilar_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_micropapilar_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_papilar_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_papilar_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_solido_pth': {
        'csv_path': 'environ/csv/dataset_carcinoma_ductal_in_situ_patrones_arquitectonicos_solido_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },

    # Balanced (pth) tasks — imbalance-capped datasets (csv in environ/csv_balance/).
    # Splits live in environ/splits/<task>_pth_balance_100. Features are a subset of
    # the full set, so data_dir stays 'features'. Use with --auto-label-dict.
    'tipo_histologico_4clases_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_tipo_histologico_4clases_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_grado_nuclear_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_carcinoma_ductal_insitu_grado_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_necrosis_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_carcinoma_ductal_insitu_necrosis_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'carcinoma_ductal_insitu_presente_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_carcinoma_ductal_insitu_presente_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_cribiforme_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_cdis_patron_cribiforme_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_micropapilar_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_cdis_patron_micropapilar_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_papilar_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_cdis_patron_papilar_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'cdis_patron_solido_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_cdis_patron_solido_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_aplica_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_grado_histologico_aplica_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_diferenciacion_tubular_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_grado_histologico_diferenciacion_tubular_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_grado_general_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_grado_histologico_grado_general_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_pleomorfismo_nuclear_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_grado_histologico_pleomorfismo_nuclear_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'grado_histologico_mitotic_rate_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_grado_histologico_mitotic_rate_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'invasion_linfatica_vascular_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_invasion_linfatica_vascular_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_en_carcinoma_invasivo_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_microcalcificaciones_en_carcinoma_invasivo_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_en_cdis_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_microcalcificaciones_en_cdis_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
    'microcalcificaciones_en_tejido_no_neoplasico_pth_balance': {
        'csv_path': 'environ/csv_balance/dataset_microcalcificaciones_en_tejido_no_neoplasico_label.csv',
        'data_dir': 'features',
        'label_dict': {},
    },
}

########################################################
def create_label_dict(csv_path=None, label_col='label'):
    """
    Genera el label_dict desde el archivo CSV de forma dinámica.

    Args:
        csv_path: Path al archivo CSV.
        label_col: Nombre de la columna que contiene la label.

    Returns:
        dict: Mapea el string del label a su índice entero.
        
    """
    
    if not csv_path or csv_path.strip() == '':
        raise ValueError(f"CSV path is empty. Cannot auto-generate label_dict.")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file {csv_path}: {str(e)}")

    if label_col not in df.columns:
        raise KeyError(
            f"Label column '{label_col}' not found in CSV. "
            f"Available columns: {list(df.columns)}"
        )

    unique_labels = df[label_col].dropna().unique()

    if len(unique_labels) == 0:
        raise ValueError(f"No valid labels found in column '{label_col}' of {csv_path}")

    unique_labels = [str(label).strip() for label in unique_labels]

    unique_labels = sorted(set(unique_labels))

    label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}

    print("\n" + "="*60)
    print("AUTO-GENERATED LABEL DICTIONARY")
    print("="*60)
    print(f"CSV Path: {csv_path}")
    print(f"Label Column: {label_col}")
    print(f"Number of Classes: {len(label_to_idx)}")
    print("\nLabel Mapping (alphabetically sorted):")
    for label, idx in label_to_idx.items():
        print(f"  '{label}': {idx}")
    print("="*60 + "\n")

    return label_to_idx

def main(args):
    # create results directory if necessary
    if not os.path.isdir(args.results_dir):
        os.mkdir(args.results_dir)

    if args.k_start == -1:
        start = 0
    else:
        start = args.k_start
    if args.k_end == -1:
        end = args.k
    else:
        end = args.k_end

    all_test_auc = []
    all_val_auc = []
    all_test_acc = []
    all_val_acc = []
    folds = np.arange(start, end)
    for i in folds:
        seed_torch(args.seed)
        train_dataset, val_dataset, test_dataset = dataset.return_splits(from_id=False, # Esta función crea los splits creo.
                csv_path='{}/splits_{}.csv'.format(args.split_dir, i))
        
        datasets = (train_dataset, val_dataset, test_dataset)
        results, test_auc, val_auc, test_acc, val_acc  = train(datasets, i, args) # Se manda args (de ahi obtiene embedding por ejemplo)
        all_test_auc.append(test_auc)
        all_val_auc.append(val_auc)
        all_test_acc.append(test_acc)
        all_val_acc.append(val_acc)
        #write results to pkl
        filename = os.path.join(args.results_dir, 'split_{}_results.pkl'.format(i))
        save_pkl(filename, results)

    final_df = pd.DataFrame({'folds': folds, 'test_auc': all_test_auc, 
        'val_auc': all_val_auc, 'test_acc': all_test_acc, 'val_acc' : all_val_acc})

    if len(folds) != args.k:
        save_name = 'summary_partial_{}_{}.csv'.format(start, end)
    else:
        save_name = 'summary.csv'
    final_df.to_csv(os.path.join(args.results_dir, save_name))

########################################################

# Generic training settings
parser = argparse.ArgumentParser(description='Configurations for WSI Training')
parser.add_argument('--data_root_dir', type=str, default=None,
                    help='data directory')
parser.add_argument('--supervised_dir', type=str, default=None,
                    help='directory containing supervised positive patch features (pt_files/{slide_id}.pt); optional')
parser.add_argument('--embed_dim', type=int, default=1024)
parser.add_argument('--max_epochs', type=int, default=200,
                    help='maximum number of epochs to train (default: 200)')
parser.add_argument('--lr', type=float, default=1e-4,
                    help='learning rate (default: 0.0001)')
parser.add_argument('--label_frac', type=float, default=1.0,
                    help='fraction of training labels (default: 1.0)')
parser.add_argument('--reg', type=float, default=1e-5,
                    help='weight decay (default: 1e-5)')
parser.add_argument('--seed', type=int, default=1, 
                    help='random seed for reproducible experiment (default: 1)')
parser.add_argument('--k', type=int, default=10, help='number of folds (default: 10)')
parser.add_argument('--k_start', type=int, default=-1, help='start fold (default: -1, last fold)')
parser.add_argument('--k_end', type=int, default=-1, help='end fold (default: -1, first fold)')
parser.add_argument('--results_dir', default='./results', help='results directory (default: ./results)')
parser.add_argument('--split_dir', type=str, default=None, 
                    help='manually specify the set of splits to use, ' 
                    +'instead of infering from the task and label_frac argument (default: None)')
parser.add_argument('--log_data', action='store_true', default=False, help='log data using tensorboard')
parser.add_argument('--testing', action='store_true', default=False, help='debugging tool')
parser.add_argument('--early_stopping', action='store_true', default=False, help='enable early stopping')
parser.add_argument('--opt', type=str, choices = ['adam', 'sgd'], default='adam')
parser.add_argument('--drop_out', type=float, default=0.25, help='dropout')
parser.add_argument('--bag_loss', type=str, choices=['svm', 'ce'], default='ce',
                     help='slide-level classification loss function (default: ce)')
parser.add_argument('--model_type', type=str,
                    choices=['clam_sb', 'clam_mb', 'clam_wdm', 'mil', 'dtfd_mil'],
                    default='clam_sb',
                    help='type of model (default: clam_sb)')
parser.add_argument('--exp_code', type=str, help='experiment code for saving results')
parser.add_argument('--weighted_sample', action='store_true', default=False, help='enable weighted sampling')
parser.add_argument('--model_size', type=str, choices=['small', 'big'], default='small', help='size of model, does not affect mil')
parser.add_argument('--task', type=str, help='Task name defined in TASK_CONFIGS')

### CLAM specific options
parser.add_argument('--no_inst_cluster', action='store_true', default=False,
                     help='disable instance-level clustering')
parser.add_argument('--inst_loss', type=str, choices=['svm', 'ce', None], default=None,
                     help='instance-level clustering loss function (default: None)')
parser.add_argument('--subtyping', action='store_true', default=False, 
                     help='subtyping problem') #! Este parámetro parece ser el encargado de mejorar la atención de parches (subtyping == categorias mutuamente excluyentes)
parser.add_argument('--bag_weight', type=float, default=0.7,
                    help='clam: weight coefficient for bag-level loss (default: 0.7)')
parser.add_argument('--B', type=int, default=8, help='numbr of positive/negative patches to sample for clam')

### Environ Arguments
parser.add_argument('--auto-label-dict', action='store_true',
                    help='Automatically generate label_dict from CSV unique labels (sorted alphabetically). '
                         'Overrides label_dict in TASK_CONFIGS.')
parser.add_argument("--pcgrad", action="store_true", default=False)
parser.add_argument('--log_gradients', action='store_true', default=False,
                    help='Log gradient interaction between slide loss and instance loss')
parser.add_argument(
    "--confidence_penalty",
    type=float,
    default=0.0,
    help="Penaliza predicciones demasiado confiadas. Recomendado probar 0.001, 0.005, 0.01"
)
parser.add_argument(
    "--use_mammoth",
    action="store_true",
    default=False,
    help="Usar MAMMOTH como reemplazo de la primera capa lineal de CLAM."
)

parser.add_argument(
    "--mammoth_num_experts",
    type=int,
    default=30,
    help="Número de expertos de MAMMOTH."
)

parser.add_argument(
    "--mammoth_num_slots",
    type=int,
    default=10,
    help="Número de slots por experto en MAMMOTH."
)

parser.add_argument(
    "--mammoth_num_heads",
    type=int,
    default=16,
    help="Número de heads de MAMMOTH."
)

parser.add_argument(
    "--mammoth_slot_dim",
    type=int,
    default=256,
    help="Dimensión de slots de MAMMOTH."
)

### DTFD-MIL specific options
parser.add_argument(
    "--num_pseudo_bags",
    type=int,
    default=8,
    help="DTFD-MIL: número de pseudo-bags en que se divide la WSI (default: 8)."
)
parser.add_argument(
    "--pseudo_bag_size",
    type=int,
    default=None,
    help="DTFD-MIL: tamaño fijo de cada pseudo-bag (default: None → división equitativa)."
)
parser.add_argument(
    "--distill_temperature",
    type=float,
    default=3.0,
    help="DTFD-MIL: temperatura para la pérdida de destilación (default: 3.0)."
)
parser.add_argument(
    "--distill_weight",
    type=float,
    default=0.5,
    help="DTFD-MIL: peso del término KL vs. CE duro en la pérdida de destilación (default: 0.5)."
)

### LR scheduler / class weighting (campaña papilar)
parser.add_argument(
    "--scheduler",
    type=str,
    choices=["none", "plateau", "cosine"],
    default="none",
    help="LR scheduler: 'none' (constante), 'plateau' (ReduceLROnPlateau sobre val_loss), "
         "'cosine' (CosineAnnealingLR sobre max_epochs). Default: none."
)
parser.add_argument(
    "--class_weight_pos",
    type=float,
    default=None,
    help="Solo binario (n_classes==2) + bag_loss=ce: peso de la clase positiva en CrossEntropyLoss "
         "(la negativa queda en 1.0). Sobrescribe --auto_class_weights. Default: None (sin override)."
)

args = parser.parse_args()
device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

def seed_torch(seed=7):
    import random
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if device.type == 'cuda':
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed) # if you are using multi-GPU.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

seed_torch(args.seed)

encoding_size = 1024
settings = {'num_splits': args.k, 
            'k_start': args.k_start,
            'k_end': args.k_end,
            'task': args.task,
            'max_epochs': args.max_epochs, 
            'results_dir': args.results_dir, 
            'lr': args.lr,
            'experiment': args.exp_code,
            'reg': args.reg,
            'label_frac': args.label_frac,
            'bag_loss': args.bag_loss,
            'seed': args.seed,
            'model_type': args.model_type,
            'model_size': args.model_size,
            "use_drop_out": args.drop_out,
            'weighted_sample': args.weighted_sample,
            'scheduler': args.scheduler,
            'class_weight_pos': args.class_weight_pos,
            'opt': args.opt}

if args.model_type in ['clam_sb', 'clam_mb', 'clam_wdm']:
   settings.update({'bag_weight': args.bag_weight,
                    'inst_loss': args.inst_loss,
                    'B': args.B})

if args.model_type == 'dtfd_mil':
    settings.update({
        'bag_weight':         args.bag_weight,
        'num_pseudo_bags':    args.num_pseudo_bags,
        'distill_temperature': args.distill_temperature,
        'distill_weight':     args.distill_weight,
    })

print('\nLoad Dataset')

if args.task not in TASK_CONFIGS:
    available = ', '.join(TASK_CONFIGS.keys())
    raise NotImplementedError(
        f"Task '{args.task}' not found in TASK_CONFIGS. "
        f"Available tasks: {available}"
    )


task_config = TASK_CONFIGS[args.task]

if args.auto_label_dict:
    label_col = task_config.get('label_col', 'label')

    try:
        auto_label_dict = create_label_dict(
            csv_path=task_config['csv_path'],
            label_col=label_col
        )

        original_label_dict = task_config.get('label_dict', {})
        task_config['label_dict'] = auto_label_dict

        if original_label_dict:
            print(f"NOTE: Overriding existing label_dict for task '{args.task}'")
            print(f"Original had {len(original_label_dict)} classes, auto-generated has {len(auto_label_dict)} classes\n")
        else:
            print(f"NOTE: Task '{args.task}' had no label_dict defined. Using auto-generated mapping.\n")

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"\nERROR: Failed to auto-generate label_dict for task '{args.task}'")
        print(f"Reason: {str(e)}")
        print(f"\nPlease ensure:")
        print(f"  1. CSV path is specified in TASK_CONFIGS['{args.task}']['csv_path']")
        print(f"  2. CSV file exists at the specified path")
        print(f"  3. CSV has a '{label_col}' column with valid labels")
        raise SystemExit(1)

if not task_config.get('label_dict'):
    raise ValueError(
        f"Task '{args.task}' has no label_dict defined. "
        f"Either add label_dict to TASK_CONFIGS or use --auto-label-dict flag."
    )

label_values = sorted(task_config['label_dict'].values())
expected_values = list(range(len(label_values)))
if label_values != expected_values:
    print(f"\nWARNING: label_dict values are not sequential 0-indexed integers.")
    print(f"Expected: {expected_values}")
    print(f"Got: {label_values}")
    print(f"This may cause issues in test_split_gen reverse mapping.\n")

args.n_classes = len(set(task_config['label_dict'].values()))

dataset_kwargs = {
    'csv_path': task_config['csv_path'],
    'data_dir': os.path.join(args.data_root_dir, task_config['data_dir']),
    'supervised_dir': args.supervised_dir,
    'shuffle': False,
    'seed': args.seed,
    'print_info': True,
    'label_dict': task_config['label_dict'],
    'patient_strat': False,
    'ignore': [],
}

# This only if the label column is different from "label"
if 'label_col' in task_config: 
    dataset_kwargs['label_col'] = task_config['label_col']

dataset = Generic_MIL_Dataset(**dataset_kwargs)


if args.task == 'task_2_tumor_subtyping':
    if args.model_type in ['clam_sb', 'clam_mb', 'clam_wdm']:
        assert args.subtyping

    
if not os.path.isdir(args.results_dir):
    os.mkdir(args.results_dir)

args.results_dir = os.path.join(args.results_dir, str(args.exp_code) + '_s{}'.format(args.seed))
if not os.path.isdir(args.results_dir):
    os.mkdir(args.results_dir)

if args.split_dir is None:
    args.split_dir = os.path.join('splits', args.task+'_{}'.format(int(args.label_frac*100)))
else:
    args.split_dir = args.split_dir

print('split_dir: ', args.split_dir)
assert os.path.isdir(args.split_dir)

settings.update({'split_dir': args.split_dir})


with open(args.results_dir + '/experiment_{}.txt'.format(args.exp_code), 'w') as f:
    print(settings, file=f)
f.close()

print("################# Settings ###################")
for key, val in settings.items():
    print("{}:  {}".format(key, val))        

if __name__ == "__main__":
    results = main(args)
    print("finished!")
    print("end script")


