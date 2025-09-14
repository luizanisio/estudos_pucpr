# arquivo: util_dados.py
import json
from typing import List
from pathlib import Path
import os

def gerar_dados_jsonl(arquivo: str, n: int) -> None:
    """
    Gera um arquivo JSONL com n registros reproduzíveis.
    Cada linha é um JSON com: Matricula (9 dígitos), Nome, Salario, CodigoSetor, Idade.

    Regras de reprodutibilidade (determinísticas):
    - Matrícula: zero-padded a 9 dígitos a partir do índice (000000000, 000000001, ...).
    - Nome: combinação determinística de listas fixas (primeiro, meio e sobrenome).
    - Salário: valor em [1500.00, 25000.00] via congruência linear sobre o índice.
    - Código do Setor: escolhe de lista fixa, ciclando deterministicamente.
    - Idade: inteiro em [18, 65] por aritmética modular sobre o índice.

    * Ao final da geração, os dados são ordenados pelo código do setor + nome para que a matrícula não seja sequencial.
    """
    primeiros_nomes: List[str] = [
        "Ana","Bruno","Carla","Diego","Eduarda","Felipe","Gabriela","Henrique","Isabela","João",
        "Karen","Lucas","Mariana","Nicolas","Olívia","Paulo","Queila","Rafael","Sofia","Tiago",
        "Úrsula","Vitor","Wagner","Xênia","Yasmin","Zeca","Bianca","Caio","Daniela","Elaine",
        "Fábio","Gustavo","Heloísa","Ian","Júlia","Leandro","Marta","Natália","Otávio","Patrícia",
        "Renato","Sérgio","Talita","Ubirajara","Valentina","William","Yuri","Zuleica","Alice","Bernardo"
    ]
    nomes_meio: List[str] = [
        "Almeida","Barros","Cardoso","Dantas","Esteves","Ferraz","Gonçalves","Heitor","Ibrahim","Junqueira",
        "Klein","Lourenço","Machado","Nogueira","Oliveira","Pereira","Queiroz","Ramos","Silva","Teixeira",
        "Uchoa","Vasconcelos","Werneck","Xavier","Yamada","Zanetti","Andrade","Bittencourt","Castro","Dias",
        "Farias","Garcia","Henriques","Iglesias","Jacob","Leal","Martins","Novaes","Ortega","Prado",
        "Quintana","Rocha","Souza","Tavares","Ulhoa","Vieira","Watanabe","Ximenes","Youssef","Zucolotto"
    ]
    sobrenomes: List[str] = [
        "Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Almeida","Costa","Gomes","Ribeiro",
        "Carvalho","Lima","Barbosa","Rocha","Dias","Nunes","Moreira","Teixeira","Correia","Cardoso",
        "Pinto","Araújo","Cruz","Melo","Castro","Fernandes","Vieira","Andrade","Sales","Cavalcanti",
        "Meireles","Peixoto","Moura","Macedo","Figueiredo","Mendes","Batista","Ramos","Pires","Prado",
        "Freitas","Matos","Machado","Assis","Camargo","Mesquita","Queiroz","Xavier","Amaral","Rezende"
    ]

    codigos_setor: List[int] = [101, 102, 103, 104, 105, 201, 202, 203, 301, 302, 401, 402]

    # Parâmetros determinísticos para salário (centavos para evitar ruído de float)
    SAL_MIN = 1500_00
    SAL_MAX = 25000_00
    SAL_RANGE = SAL_MAX - SAL_MIN
    MUL = 37_123
    INC = 9_871
    MOD = 100_003

    path = Path(arquivo)
    path.parent.mkdir(parents=True, exist_ok=True)

    dados = []
    for i in range(n):
        matricula = f"{i:06d}"

        p = primeiros_nomes[i % len(primeiros_nomes)]
        m = nomes_meio[(i // len(primeiros_nomes)) % len(nomes_meio)]
        s = sobrenomes[(i // (len(primeiros_nomes) * len(nomes_meio))) % len(sobrenomes)]
        nome = f"{p} {m} {s}"

        # Sequência congruente linear para espalhar salários de forma estável
        seq = (MUL * (i + 1) + INC) % MOD
        sal_centavos = SAL_MIN + (seq % (SAL_RANGE + 1))
        salario = round(sal_centavos / 100.0, 2)

        codigo_setor = codigos_setor[i % len(codigos_setor)]
        idade = 18 + ((i * 7 + 11) % (65 - 18 + 1))

        registro = { "Matricula": matricula,      "Nome": nome,  "Salario": salario,
                     "CodigoSetor": codigo_setor, "Idade": idade, }
        dados.append(registro)

    print(f'Número de registros gerados:', len(dados))
    # Gravando o arquivo final
    with path.open("w", encoding="utf-8") as f:
        for registro in sorted(dados, key=lambda x: (x["CodigoSetor"], x["Nome"])):
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print(f'Registros gravados no arquivo:', arquivo)
    print(f'Máximo de registros com nomes diferentes:', len(primeiros_nomes)*len(nomes_meio)*len(sobrenomes))


def get_dados(qtd = 1000, path = './dados'):
    if not os.path.isdir(path):
        os.makedirs(path)
    arquivo = f'dados_{qtd}.json'
    arquivo = os.path.join(path, arquivo)
    if not os.path.isfile(arquivo):
        print(f'Gerando arquivo com {qtd} dados ...')
        gerar_dados_jsonl(arquivo, qtd)
    dados = open(arquivo, 'r', encoding='utf-8').readlines()
    dados = [json.loads(d) for d in dados]
    print(f'Arquivo com {qtd} dados carregados _o/')
    print(f'Exemplo: {dados[0]}')
    print('='*60)
    return dados

if __name__ == "__main__":
    # Gera arquivos de dados padrão para o experimento
    for qtd in (1000, 5000, 10000, 50000, 100000):
        gerar_dados_jsonl(f'dados_{qtd}.json', qtd)
