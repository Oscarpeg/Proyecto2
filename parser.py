import json
from collections import defaultdict

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens + [{"tipo": "$", "valor": "$", "linea": -1, "col": -1}]
        self.indice = 0
        self.token_actual = self.tokens[self.indice] if self.tokens else None

        print("Cargando gramática desde 'gramatica.txt'...")
        self.gramatica = self.cargar_gramatica("gramatica.txt")
        print("Gramática cargada.")

        self.PRIMEROS = self.calcular_primeros()
        print("PRIMEROS calculados:", self.PRIMEROS)

        self.SIGUIENTES = self.calcular_siguientes()
        print("SIGUIENTES calculados:", self.SIGUIENTES)

        try:
            print("Cargando tabla LL(1) desde 'tabla_ll1.json'...")
            with open("tabla_ll1.json", "r", encoding="utf-8") as f:
                self.tabla_ll1 = json.load(f)
            print("Tabla LL(1) cargada.")
        except Exception as e:
            print("❌ Error al cargar tabla LL(1):", e)
            self.tabla_ll1 = {}

        if "Programa" not in self.tabla_ll1:
            print("⚠️ Advertencia: 'Programa' no está en la tabla LL(1).")
        else:
            print("✅ 'Programa' encontrado en la tabla LL(1).")

    def cargar_gramatica(self, archivo):
        gramatica = defaultdict(list)
        try:
            with open(archivo, 'r') as f:
                for linea in f:
                    if not linea.strip():
                        continue
                    cabeza, cuerpo = linea.strip().split("::=")
                    cabeza = cabeza.strip().strip("<>")
                    producciones = cuerpo.strip().split("|")
                    for prod in producciones:
                        simbolos = prod.strip().split()
                        gramatica[cabeza].append(simbolos)
        except Exception as e:
            print(f" Error al cargar gramática: {e}")
            return {}
        return gramatica

    def obtener_todos_los_no_terminales(self, gramatica):
        no_terminales = set(gramatica.keys())
        for producciones in gramatica.values():
            for prod in producciones:
                for simbolo in prod:
                    if simbolo.isalpha() and simbolo in gramatica:
                        no_terminales.add(simbolo)
        return no_terminales

    def calcular_primeros(self):
        primeros = defaultdict(set)
        no_terminales = self.obtener_todos_los_no_terminales(self.gramatica)

        def primero_de(simbolo, visitando):
            if simbolo not in self.gramatica:  # terminal
                return {simbolo}
            if simbolo in visitando:
                return set()
            visitando.add(simbolo)

            for produccion in self.gramatica.get(simbolo, []):
                for s in produccion:
                    primeros_simbolo = primero_de(s, visitando)
                    primeros[simbolo] |= primeros_simbolo - {'ε'}
                    if 'ε' not in primeros_simbolo:
                        break
                else:
                    primeros[simbolo].add('ε')

            visitando.remove(simbolo)
            return primeros[simbolo]

        for nt in no_terminales:
            primero_de(nt, set())

        return primeros

    def calcular_siguientes(self):
        siguientes = defaultdict(set)
        simbolo_inicial = list(self.gramatica.keys())[0]
        siguientes[simbolo_inicial].add('$')

        cambiado = True
        while cambiado:
            cambiado = False
            for cabeza, producciones in self.gramatica.items():
                for prod in producciones:
                    for i, B in enumerate(prod):
                        if B in self.gramatica:
                            beta = prod[i+1:]
                            primero_beta = self.calcular_primero_beta(beta)
                            anterior = len(siguientes[B])
                            siguientes[B] |= primero_beta - {'ε'}
                            if 'ε' in primero_beta or not beta:
                                siguientes[B] |= siguientes[cabeza]
                            if len(siguientes[B]) != anterior:
                                cambiado = True
        return siguientes

    def calcular_primero_beta(self, beta):
        resultado = set()
        for s in beta:
            resultado |= self.PRIMEROS[s] - {'ε'}
            if 'ε' not in self.PRIMEROS[s]:
                break
        else:
            resultado.add('ε')
        return resultado

    def construir_tabla_ll1(self):
        tabla = defaultdict(dict)
        for cabeza, producciones in self.gramatica.items():
            for prod in producciones:
                primero_prod = self.calcular_primero_beta(prod)
                for t in primero_prod:
                    if t != 'ε':
                        tabla[cabeza][t] = prod
                if 'ε' in primero_prod:
                    for t in self.SIGUIENTES[cabeza]:
                        tabla[cabeza][t] = prod
        return tabla

    def parse(self):
        print("Iniciando análisis sintáctico...")
        resultado = self.parse_ll1("Programa")
        print("Análisis completado.")
        return resultado

    def parse_ll1(self, simbolo_inicial="Programa"):
        pila = ["$", simbolo_inicial]
        paso = 1

        print("\n--- INICIO DEL ANÁLISIS SINTÁCTICO LL(1) ---\n")
        while pila:
            cima = pila.pop()
            actual = self.tokens[self.indice]
            actual_tipo = actual["tipo"]

            print(f"Paso {paso}:")
            print(f"  Pila: {pila + [cima]}")
            print(f"  Token actual: {actual_tipo} (lexema: '{actual['valor']}')")

            if cima == "$" and actual_tipo == "$":
                print("\n✔️ Análisis exitoso: la cadena ha sido aceptada.\n")
                self.escribir_resultado("La cadena fue aceptada correctamente.\n")
                return True

            elif cima not in self.gramatica:  # Terminal
                if cima == actual_tipo:
                    print(f"   Terminal coincide: '{cima}'\n")
                    self.indice += 1
                    if self.indice < len(self.tokens):
                        self.token_actual = self.tokens[self.indice]
                else:
                    print(f"   Error: se esperaba '{cima}', pero se encontró '{actual_tipo}'.\n")
                    self.reportar_error(cima, actual_tipo, actual)
                    return False

            elif cima in self.tabla_ll1:
                producciones = self.tabla_ll1[cima]
                if actual_tipo not in producciones:
                    print(f"   Error: no hay producción para ({cima}, {actual_tipo}).\n")
                    self.reportar_error(cima, actual_tipo, actual)
                    return False

                produccion = producciones[actual_tipo]
                print(f"   Producción aplicada: {cima} → {' '.join(produccion)}")
                for simbolo in reversed(produccion):
                    if simbolo != "ε":
                        pila.append(simbolo)
                print(f"   Pila actualizada: {pila}\n")

            else:
                print(f"   Error: no se reconoce el símbolo no terminal '{cima}'.\n")
                self.reportar_error(cima, actual_tipo, actual)
                return False

            paso += 1

        print("\n❌ Análisis incompleto: la pila se vació sin aceptar toda la entrada.\n")
        return False

    def reportar_error(self, esperado, tipo_encontrado, token_encontrado):
        fila = token_encontrado.get("linea", -1)
        col = token_encontrado.get("col", -1)
        lexema = token_encontrado.get("valor", "")
        mensaje_error = f"<{fila},{col}> Error sintáctico: se encontró: \"{lexema}\"; se esperaba: \"{esperado}\".\n"
        self.escribir_resultado(mensaje_error)

    def escribir_resultado(self, mensaje):
        with open("resultado.txt", "w", encoding="utf-8") as f:
            f.write(mensaje)

