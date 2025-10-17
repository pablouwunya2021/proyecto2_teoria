import copy
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class Grammar:
    """
    Clase para representar una gramática libre de contexto.
    Maneja producciones, terminales, no terminales y símbolo inicial.
    """
    
    def __init__(self):
        self.productions = defaultdict(list)  # Dict[str, List[List[str]]]
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
    
    def add_production(self, left: str, right: List[str]):
        """
        Añade una producción a la gramática.
        
        Args:
            left (str): Símbolo no terminal del lado izquierdo
            right (List[str]): Lista de símbolos del lado derecho
        """
        if not isinstance(right, list):
            raise ValueError("El lado derecho debe ser una lista de símbolos")
        
        self.productions[left].append(right)
        self.non_terminals.add(left)
        
        # Clasificar símbolos del lado derecho
        for symbol in right:
            # Consideramos terminales a los símbolos que:
            # - No están en mayúsculas (convención)
            # - O son símbolos especiales como epsilon
            if (symbol and not symbol[0].isupper()) or symbol in ['epsilon', 'ε', '']:
                self.terminals.add(symbol)
            else:
                # Los símbolos que empiezan con mayúscula se consideran no terminales
                # (se añadirán cuando se definan sus producciones)
                pass
    
    def set_start_symbol(self, symbol: str):
        """
        Establece el símbolo inicial de la gramática.
        
        Args:
            symbol (str): Símbolo inicial
        """
        self.start_symbol = symbol
        self.non_terminals.add(symbol)
    
    def is_in_cnf(self) -> bool:
        """
        Verifica si la gramática está en Forma Normal de Chomsky.
        
        Returns:
            bool: True si está en CNF, False en caso contrario
        """
        if not self.start_symbol:
            return False
        
        for var, productions in self.productions.items():
            for prod in productions:
                # Producción vacía solo permitida para el símbolo inicial
                if not prod:
                    if var != self.start_symbol:
                        return False
                    continue
                
                # Producción con un símbolo
                if len(prod) == 1:
                    # Debe ser un terminal
                    if prod[0] not in self.terminals:
                        return False
                
                # Producción con dos símbolos
                elif len(prod) == 2:
                    # Ambos deben ser no terminales
                    if prod[0] not in self.non_terminals or prod[1] not in self.non_terminals:
                        return False
                
                # Producciones con más de dos símbolos no están permitidas en CNF
                else:
                    return False
        
        return True
    
    def print_grammar(self):
        """
        Imprime la gramática de forma legible.
        """
        print(f"Símbolo inicial: {self.start_symbol}")
        print(f"No terminales: {sorted(self.non_terminals)}")
        print(f"Terminales: {sorted(self.terminals)}")
        print("Producciones:")
        
        for var in sorted(self.productions.keys()):
            productions_str = []
            for prod in self.productions[var]:
                if not prod:
                    productions_str.append("ε")
                else:
                    productions_str.append(" ".join(prod))
            
            print(f"  {var} -> {' | '.join(productions_str)}")
    
    def copy(self):
        """
        Crea una copia profunda de la gramática.
        
        Returns:
            Grammar: Nueva instancia de Grammar con los mismos datos
        """
        new_grammar = Grammar()
        new_grammar.start_symbol = self.start_symbol
        new_grammar.terminals = self.terminals.copy()
        new_grammar.non_terminals = self.non_terminals.copy()
        
        # Copia profunda de las producciones
        for var, productions in self.productions.items():
            new_grammar.productions[var] = [prod.copy() for prod in productions]
        
        return new_grammar
    
    def get_terminals_from_string(self, symbols: List[str]) -> Set[str]:
        """
        Extrae los terminales de una lista de símbolos.
        
        Args:
            symbols (List[str]): Lista de símbolos
            
        Returns:
            Set[str]: Conjunto de terminales encontrados
        """
        terminals = set()
        for symbol in symbols:
            if symbol in self.terminals:
                terminals.add(symbol)
        return terminals
    
    def get_non_terminals_from_string(self, symbols: List[str]) -> Set[str]:
        """
        Extrae los no terminales de una lista de símbolos.
        
        Args:
            symbols (List[str]): Lista de símbolos
            
        Returns:
            Set[str]: Conjunto de no terminales encontrados
        """
        non_terminals = set()
        for symbol in symbols:
            if symbol in self.non_terminals:
                non_terminals.add(symbol)
        return non_terminals
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Valida la gramática y retorna errores si los hay.
        
        Returns:
            Tuple[bool, List[str]]: (es_válida, lista_de_errores)
        """
        errors = []
        
        if not self.start_symbol:
            errors.append("No se ha definido un símbolo inicial")
        
        if not self.productions:
            errors.append("No se han definido producciones")
        
        if self.start_symbol and self.start_symbol not in self.productions:
            errors.append(f"El símbolo inicial '{self.start_symbol}' no tiene producciones")
        
        # Verificar que todos los no terminales en las producciones tengan definiciones
        used_non_terminals = set()
        for var, productions in self.productions.items():
            for prod in productions:
                for symbol in prod:
                    if symbol not in self.terminals and symbol:
                        used_non_terminals.add(symbol)
        
        undefined_non_terminals = used_non_terminals - set(self.productions.keys())
        if undefined_non_terminals:
            errors.append(f"No terminales sin definición: {sorted(undefined_non_terminals)}")
        
        return len(errors) == 0, errors
    
    def get_stats(self) -> Dict:
        """
        Retorna estadísticas de la gramática.
        
        Returns:
            Dict: Diccionario con estadísticas
        """
        total_productions = sum(len(prods) for prods in self.productions.values())
        
        return {
            'non_terminals_count': len(self.non_terminals),
            'terminals_count': len(self.terminals),
            'total_productions': total_productions,
            'variables_with_productions': len(self.productions),
            'start_symbol': self.start_symbol,
            'is_cnf': self.is_in_cnf()
        }
    
    def remove_production(self, left: str, right: List[str]):
        """
        Remueve una producción específica.
        
        Args:
            left (str): No terminal del lado izquierdo
            right (List[str]): Producción del lado derecho a remover
        """
        if left in self.productions and right in self.productions[left]:
            self.productions[left].remove(right)
            
            # Si no quedan producciones para este no terminal, removerlo
            if not self.productions[left]:
                del self.productions[left]
                if left != self.start_symbol:
                    self.non_terminals.discard(left)
    
    def has_epsilon_productions(self) -> bool:
        """
        Verifica si la gramática tiene producciones epsilon.
        
        Returns:
            bool: True si tiene producciones epsilon
        """
        for productions in self.productions.values():
            for prod in productions:
                if not prod or (len(prod) == 1 and prod[0] in ['ε', 'epsilon', '']):
                    return True
        return False
    
    def has_unit_productions(self) -> bool:
        """
        Verifica si la gramática tiene producciones unitarias.
        
        Returns:
            bool: True si tiene producciones unitarias
        """
        for productions in self.productions.values():
            for prod in productions:
                if len(prod) == 1 and prod[0] in self.non_terminals:
                    return True
        return False
    
    def __str__(self) -> str:
        """
        Representación en string de la gramática.
        """
        lines = [f"Grammar(start='{self.start_symbol}')"]
        for var in sorted(self.productions.keys()):
            productions_str = []
            for prod in self.productions[var]:
                if not prod:
                    productions_str.append("ε")
                else:
                    productions_str.append(" ".join(prod))
            lines.append(f"  {var} -> {' | '.join(productions_str)}")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return self.__str__()