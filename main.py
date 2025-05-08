from lexer import lexer
from parser import Parser
import sys

# Limpiar el archivo de resultados al inicio
open("resultado.txt", "w").close()

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.py")
        return

    input_file = sys.argv[1]
    output_file = "resultado.txt"

    try:
        with open(input_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"No se pudo encontrar el archivo: {input_file}")
        return

    tokens = lexer(source_code)
    print("Tokens:")
    for t in tokens:
        print(t)
    if tokens is None:
        with open(output_file, 'w') as f:
            f.write(">>> Error léxico. No se pudo continuar con el análisis sintáctico.\n")
        return

    parser = Parser(tokens)

    # PRIMEROS
    primeros = parser.calcular_primeros()
    with open(output_file, 'a', encoding="utf-8") as f:
        f.write("Conjuntos PRIMEROS:\n")
        for nt, conjunto in primeros.items():
            f.write(f"{nt}: {conjunto}\n")
        f.write("\n")

    # SIGUIENTES
    siguientes = parser.calcular_siguientes()
    with open(output_file, 'a', encoding="utf-8") as f:
        f.write("Conjuntos SIGUIENTES:\n")
        for nt, conjunto in siguientes.items():
            f.write(f"{nt}: {conjunto}\n")
        f.write("\n")

    # Análisis sintáctico
    try:
        parser.parse()  # Asegúrate de que 'parse' esté correctamente implementado
        with open(output_file, 'a', encoding="utf-8") as f:
            f.write("El análisis sintáctico ha finalizado exitosamente.\n")
    except SyntaxError as e:
        with open(output_file, 'a', encoding="utf-8") as f:
            f.write(str(e) + "\n")

if __name__ == "__main__":
    main()

