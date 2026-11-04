"""Official orchestration entry point. `python -m src.main --all`."""
import argparse
import shutil
from .config import RAW,BRONZE,SILVER,GOLD,QUALITY,REPORTS,WAREHOUSE
from .generate_synthetic import generate
from .transform import build_bronze,build_silver,build_gold,_write_database
from .poc01_cancelamento import run as poc01
from .poc02_pre_loja import run as poc02
from .quality import run as check_quality
from .report import build as build_report


def main():
    parser=argparse.ArgumentParser(description='POC CLARO: coorte outubro/2026 e jornada 180 dias')
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--all',action='store_true',help='Gera fontes, camadas, ambas POCs e dashboard')
    group.add_argument('--generate',action='store_true',help='Somente gera os dados sintéticos')
    group.add_argument('--build',action='store_true',help='Bronze -> Silver -> Gold e qualidade, dados existentes')
    group.add_argument('--poc01',action='store_true',help='Recalcula POC 01 a partir das fontes existentes')
    group.add_argument('--poc02',action='store_true',help='Recalcula POC 02 a partir das fontes existentes')
    group.add_argument('--clean-generated',action='store_true',help='Remove camadas derivadas e outputs, nao as fontes')
    args=parser.parse_args()
    if args.clean_generated:
        for path in [BRONZE,SILVER,GOLD,QUALITY,REPORTS]:
            if path.exists(): shutil.rmtree(path)
        if WAREHOUSE.exists(): WAREHOUSE.unlink()
        print('[CLEAN] Derivados excluidos. Fontes sinteticas preservadas.')
        return
    if args.all or args.generate or not any([args.build,args.poc01,args.poc02]):
        generate()
        if args.generate:return
    build_bronze()
    raw,events=build_silver()
    payload=build_gold(raw,events)
    check_quality(payload)
    one=two=None
    if args.all or args.build or args.poc01 or not any([args.poc02]):
        one=poc01(payload)
    if args.all or args.build or args.poc02 or not any([args.poc01]):
        two=poc02(payload)
    if one and two:build_report(one,two)
    _write_database() # Materializar apos TODAS as tabelas especificas das POCs
    print('[CONCLUIDO] Saidas em data/gold, data/warehouse e reports')

if __name__=='__main__':
    main()
