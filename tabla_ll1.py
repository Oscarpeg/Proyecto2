import re
import json
from collections import defaultdict

# Leer la gramática desde el archivo
def cargar_gramatica(nombre_archivo):
    gramatica = defaultdict(list)
    with open(nombre_archivo, 'r') as f:
        for linea in f:
            if not linea.strip():
                continue
            cabeza, cuerpo = linea.strip().split("::=")
            cabeza = cabeza.strip().strip("<>")
            producciones = cuerpo.strip().split("|")
            for prod in producciones:
                simbolos = [s if not (s.startswith('"') and s.endswith('"')) else s[1:-1] for s in prod.strip().split()]

                gramatica[cabeza].append(simbolos)
    return gramatica

# Calcular PRIMERO
def calcular_primeros(gramatica):
    primeros = defaultdict(set)

    def primero_de(simbolo, visitando):
        if simbolo not in gramatica:  # terminal
            return {simbolo}
        if simbolo in visitando:  # prevención de recursión infinita
            return set()
        visitando.add(simbolo)

        for produccion in gramatica[simbolo]:
            for s in produccion:
                primeros_simbolo = primero_de(s, visitando)
                primeros[simbolo] |= primeros_simbolo - {'ε'}
                if 'ε' not in primeros_simbolo:
                    break
            else:
                primeros[simbolo].add('ε')

        visitando.remove(simbolo)
        return primeros[simbolo]

    for no_terminal in gramatica:
        primero_de(no_terminal, set())

    return primeros

# Calcular SIGUIENTE
def calcular_siguientes(gramatica, primeros, simbolo_inicial):
    siguientes = defaultdict(set)
    siguientes[simbolo_inicial].add('$')  # símbolo de fin de entrada

    cambiado = True
    while cambiado:
        cambiado = False
        for cabeza, producciones in gramatica.items():
            for prod in producciones:
                for i, B in enumerate(prod):
                    if B in gramatica:  # es no terminal
                        siguiente_original = siguientes[B].copy()
                        beta = prod[i+1:]
                        if beta:
                            primero_beta = calcular_primero_beta(beta, primeros)
                            siguientes[B] |= primero_beta - {'ε'}
                            if 'ε' in primero_beta:
                                siguientes[B] |= siguientes[cabeza]
                        else:
                            siguientes[B] |= siguientes[cabeza]
                        if siguientes[B] != siguiente_original:
                            cambiado = True
    return siguientes

def calcular_primero_beta(beta, primeros):
    resultado = set()
    for s in beta:
        resultado |= primeros[s] - {'ε'}
        if 'ε' not in primeros[s]:
            break
    else:
        resultado.add('ε')
    return resultado

# Construir la tabla LL(1)
def construir_tabla_ll1(gramatica, primeros, siguientes):
    tabla = defaultdict(dict)

    for cabeza, producciones in gramatica.items():
        for prod in producciones:
            primero_prod = calcular_primero_beta(prod, primeros)
            for t in primero_prod:
                if t != 'ε':
                    tabla[cabeza][t] = prod
            if 'ε' in primero_prod:
                for t in siguientes[cabeza]:
                    tabla[cabeza][t] = prod

    return tabla

# Guardar la tabla como JSON (ahora correctamente como listas)
def guardar_tabla(tabla, nombre_archivo):
    # Convertir defaultdict a dict estándar para serialización
    tabla_serializable = {nt: {t: p for t, p in reglas.items()} for nt, reglas in tabla.items()}
    with open(nombre_archivo, 'w') as f:
        json.dump(tabla_serializable, f, indent=4)

# === EJECUCIÓN PRINCIPAL ===
if __name__ == '__main__':
    nombre_archivo = 'gramatica.txt'
    gramatica = cargar_gramatica(nombre_archivo)
    simbolo_inicial = list(gramatica.keys())[0]
    primeros = calcular_primeros(gramatica)
    siguientes = calcular_siguientes(gramatica, primeros, simbolo_inicial)
    tabla_ll1 = construir_tabla_ll1(gramatica, primeros, siguientes)
    guardar_tabla(tabla_ll1, 'tabla_ll1.json')
    print("✅ Tabla LL(1) construida correctamente en 'tabla_ll1.json'")

