class ColorPrint:
    R = '\033[91m'
    G = '\033[92m'
    B = '\033[94m'
    C = '\033[96m'
    Y = '\033[93m'

    W = '\033[93m'+'[Aviso]: '+'\033[0m'
    E = '\033[91m'+'[Erro]:  '+'\033[0m'
    I = '\033[96m'+'[Info]:  '+'\033[0m'
    S = '\033[92m'+'[Success]:  '+'\033[0m'
    U = '\033[4m'
    B = '\033[1m'

def color(string, color):
    return str(getattr(ColorPrint, color)+str(string)+'\033[0m')
