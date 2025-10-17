import time
from typing import Dict, List, Set, Tuple, Optional
from cyk_parser import CYKParser, ParseTree
from grammar import Grammar

class EnglishGrammarCYK:
    
    def __init__(self):
        self.setup_grammar()
        self.parser = None
    
    def setup_grammar(self):
        self.grammar = Grammar()
        self.grammar.set_start_symbol('S')
        
        productions = [
            ('S', ['NP', 'VP']),
            ('VP', ['VP', 'PP']),
            ('VP', ['V', 'NP']),
            ('VP', ['cooks']),
            ('VP', ['drinks']),
            ('VP', ['eats']),
            ('VP', ['cuts']),
            ('PP', ['P', 'NP']),
            ('NP', ['Det', 'N']),
            ('NP', ['he']),
            ('NP', ['she']),
            ('V', ['cooks']),
            ('V', ['drinks']),
            ('V', ['eats']),
            ('V', ['cuts']),
            ('P', ['in']),
            ('P', ['with']),
            ('N', ['cat']),
            ('N', ['dog']),
            ('N', ['beer']),
            ('N', ['cake']),
            ('N', ['juice']),
            ('N', ['meat']),
            ('N', ['soup']),
            ('N', ['fork']),
            ('N', ['knife']),
            ('N', ['oven']),
            ('N', ['spoon']),
            ('Det', ['a']),
            ('Det', ['the']),
        ]
        
        for left, right in productions:
            self.grammar.add_production(left, right)
        
        self.terminals = {
            'he', 'she',
            'cooks', 'drinks', 'eats', 'cuts',
            'a', 'the',
            'cat', 'dog', 'beer', 'cake', 'juice', 'meat', 'soup',
            'fork', 'knife', 'oven', 'spoon',
            'in', 'with'
        }
        
        self.non_terminals = {'S', 'NP', 'VP', 'PP', 'V', 'P', 'N', 'Det'}
    
    def convert_to_proper_cnf(self):
        cnf_productions = [
            ('S', ['NP', 'VP']),
            ('VP', ['VP1', 'PP']),
            ('VP', ['V', 'NP']),
            ('VP', ['cooks']),
            ('VP', ['drinks']),
            ('VP', ['eats']),
            ('VP', ['cuts']),
            ('VP1', ['V', 'NP']),
            ('VP1', ['cooks']),
            ('VP1', ['drinks']),
            ('VP1', ['eats']),
            ('VP1', ['cuts']),
            ('PP', ['P', 'NP']),
            ('NP', ['Det', 'N']),
            ('NP', ['he']),
            ('NP', ['she']),
            ('V', ['cooks']),
            ('V', ['drinks']),
            ('V', ['eats']),
            ('V', ['cuts']),
            ('P', ['in']),
            ('P', ['with']),
            ('N', ['cat']),
            ('N', ['dog']),
            ('N', ['beer']),
            ('N', ['cake']),
            ('N', ['juice']),
            ('N', ['meat']),
            ('N', ['soup']),
            ('N', ['fork']),
            ('N', ['knife']),
            ('N', ['oven']),
            ('N', ['spoon']),
            ('Det', ['a']),
            ('Det', ['the']),
        ]
        
        self.cnf_grammar = Grammar()
        self.cnf_grammar.set_start_symbol('S')
        
        for left, right in cnf_productions:
            self.cnf_grammar.add_production(left, right)
        
        self.non_terminals.add('VP1')
        
        self.parser = CYKParser(self.cnf_grammar)
    
    def parse(self, sentence: List[str]) -> Tuple[bool, float, Optional[ParseTree]]:
        if not self.parser:
            self.convert_to_proper_cnf()
        
        return self.parser.parse(sentence)
    
    def print_table(self, sentence: List[str]):
        if self.parser:
            self.parser.print_table(sentence)
    
    def print_parse_tree(self, tree: ParseTree, sentence: List[str] = None, indent: int = 0):
        if self.parser and tree:
            self.parser.print_parse_tree(tree, indent, sentence)
    
    def save_parse_tree(self, tree: ParseTree, filename: str):
        if self.parser and tree:
            self.parser.save_parse_tree(tree, filename)
    
    def print_grammar(self):
        print("=== GRAMÁTICA DE ORACIONES EN INGLÉS ===")
        if hasattr(self, 'cnf_grammar') and self.cnf_grammar:
            self.cnf_grammar.print_grammar()
        else:
            self.grammar.print_grammar()
    
    def validate_sentence(self, sentence: List[str]) -> Tuple[bool, List[str]]:
        invalid_words = [word for word in sentence if word not in self.terminals]
        return len(invalid_words) == 0, invalid_words
    
    def get_vocabulary_info(self) -> Dict:
        vocab_by_type = {
            'pronombres': ['he', 'she'],
            'verbos': ['cooks', 'drinks', 'eats', 'cuts'],
            'determinantes': ['a', 'the'],
            'sustantivos': ['cat', 'dog', 'beer', 'cake', 'juice', 'meat', 'soup', 'fork', 'knife', 'oven', 'spoon'],
            'preposiciones': ['in', 'with']
        }
        
        return {
            'total_words': len(self.terminals),
            'by_type': vocab_by_type,
            'all_terminals': sorted(self.terminals)
        }
    
    def analyze_sentence_structure(self, sentence: List[str]) -> Dict:
        if not self.parser:
            self.convert_to_proper_cnf()
        
        accepted, parse_time, parse_tree = self.parse(sentence)
        
        if not accepted:
            return {
                'accepted': False,
                'error': 'Oración no aceptada por la gramática'
            }
        
        components = self._analyze_components(sentence)
        
        return {
            'accepted': True,
            'parse_time': parse_time,
            'sentence_length': len(sentence),
            'components': components,
            'has_prepositional_phrase': any(word in ['in', 'with'] for word in sentence),
            'verb_count': len([word for word in sentence if word in ['cooks', 'drinks', 'eats', 'cuts']]),
            'noun_count': len([word for word in sentence if word in self._get_nouns()])
        }
    
    def _analyze_components(self, sentence: List[str]) -> Dict:
        vocab_info = self.get_vocabulary_info()
        
        components = {
            'subject': [],
            'verb': [],
            'object': [],
            'prepositional_phrase': []
        }
        
        for i, word in enumerate(sentence):
            if word in vocab_info['by_type']['pronombres']:
                components['subject'].append((word, i))
            elif word in vocab_info['by_type']['verbos']:
                components['verb'].append((word, i))
            elif word in vocab_info['by_type']['preposiciones']:
                prep_phrase = sentence[i:]
                components['prepositional_phrase'].append((prep_phrase, i))
                break
        
        return components
    
    def _get_nouns(self) -> Set[str]:
        return {'cat', 'dog', 'beer', 'cake', 'juice', 'meat', 'soup', 'fork', 'knife', 'oven', 'spoon'}
    
    def generate_example_sentences(self) -> List[List[str]]:
        examples = [
            ['she', 'eats'],
            ['he', 'cooks'],
            ['she', 'drinks'],
            ['he', 'cuts'],
            ['she', 'eats', 'a', 'cake'],
            ['he', 'drinks', 'the', 'beer'],
            ['the', 'cat', 'eats', 'meat'],
            ['a', 'dog', 'drinks', 'juice'],
            ['she', 'eats', 'a', 'cake', 'with', 'a', 'fork'],
            ['he', 'cuts', 'meat', 'with', 'a', 'knife'],
            ['the', 'cat', 'drinks', 'the', 'beer', 'in', 'the', 'oven'],
            ['she', 'cooks', 'soup', 'with', 'a', 'spoon'],
            ['the', 'dog', 'eats', 'cake', 'in', 'the', 'oven'],
        ]
        
        return examples
    
    def generate_invalid_sentences(self) -> List[List[str]]:
        invalid_examples = [
            (['eats', 'she'], "Orden incorrecto: verbo antes del sujeto"),
            (['a', 'cake', 'eats', 'she'], "Orden completamente incorrecto"),
            (['eats'], "Solo verbo, falta sujeto"),
            (['a', 'cake'], "Solo objeto, faltan sujeto y verbo"),
            (['she', 'runs'], "Verbo 'runs' no está en el vocabulario"),
            (['john', 'eats'], "Nombre propio 'john' no está en el vocabulario"),
            (['she', 'eats', 'and', 'drinks'], "Conjunción 'and' no soportada"),
            (['the', 'big', 'cat', 'eats'], "Adjetivo 'big' no soportado"),
        ]
        
        return invalid_examples
    
    def run_comprehensive_test(self) -> Dict:
        print("=== PRUEBA COMPREHENSIVA DE GRAMÁTICA INGLESA ===")
        
        results = {
            'valid_sentences': [],
            'invalid_sentences': [],
            'total_time': 0,
            'summary': {}
        }
        
        start_time = time.time()
        
        print("\n1. Probando oraciones válidas...")
        valid_examples = self.generate_example_sentences()
        
        for sentence in valid_examples:
            accepted, parse_time, parse_tree = self.parse(sentence)
            results['valid_sentences'].append({
                'sentence': sentence,
                'accepted': accepted,
                'parse_time': parse_time,
                'expected': True,
                'correct': accepted == True
            })
            
            status = "✅" if accepted else "❌"
            print(f"  {status} {' '.join(sentence)} ({parse_time:.6f}s)")
            
            if accepted and parse_tree:
                try:
                    filename = f"output/parse_trees/comprehensive_valid_{'-'.join(sentence)}.json"
                    self.parser.save_parse_tree(parse_tree, filename)
                    print(f"    📁 Árbol guardado en: {filename}")
                except Exception as e:
                    print(f"    ⚠️ Error al guardar árbol: {e}")
        
        print("\n2. Probando oraciones inválidas...")
        invalid_examples = self.generate_invalid_sentences()
        
        for sentence, reason in invalid_examples:
            is_vocab_valid, invalid_words = self.validate_sentence(sentence)
            
            if is_vocab_valid:
                accepted, parse_time, parse_tree = self.parse(sentence)
            else:
                accepted, parse_time = False, 0.0
                print(f"  ⚠️  {' '.join(sentence)} - Vocabulario inválido: {invalid_words}")
                continue
            
            results['invalid_sentences'].append({
                'sentence': sentence,
                'accepted': accepted,
                'parse_time': parse_time,
                'expected': False,
                'correct': accepted == False,
                'reason': reason
            })
            
            status = "✅" if not accepted else "❌"
            print(f"  {status} {' '.join(sentence)} ({parse_time:.6f}s) - {reason}")
        
        end_time = time.time()
        results['total_time'] = end_time - start_time
        
        valid_correct = sum(1 for r in results['valid_sentences'] if r['correct'])
        invalid_correct = sum(1 for r in results['invalid_sentences'] if r['correct'])
        total_tests = len(results['valid_sentences']) + len(results['invalid_sentences'])
        total_correct = valid_correct + invalid_correct
        
        results['summary'] = {
            'total_tests': total_tests,
            'total_correct': total_correct,
            'accuracy': total_correct / total_tests if total_tests > 0 else 0,
            'valid_sentences_tested': len(results['valid_sentences']),
            'valid_sentences_correct': valid_correct,
            'invalid_sentences_tested': len(results['invalid_sentences']),
            'invalid_sentences_correct': invalid_correct,
            'average_parse_time': sum(r['parse_time'] for r in results['valid_sentences']) / len(results['valid_sentences']) if results['valid_sentences'] else 0
        }
        
        print(f"\n=== RESUMEN DE PRUEBAS ===")
        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas correctas: {total_correct}")
        print(f"Precisión: {results['summary']['accuracy']:.2%}")
        print(f"Tiempo total: {results['total_time']:.6f}s")
        print(f"Tiempo promedio por parsing: {results['summary']['average_parse_time']:.6f}s")
        
        return results

def demo_english_grammar():
    print("=== DEMO: GRAMÁTICA DE ORACIONES EN INGLÉS ===")
    print("Proyecto CYK - Teoría de la Computación 2024")
    print("-" * 60)
    
    analyzer = EnglishGrammarCYK()
    analyzer.convert_to_proper_cnf()
    
    print("\n1. INFORMACIÓN DE LA GRAMÁTICA:")
    analyzer.print_grammar()
    
    vocab_info = analyzer.get_vocabulary_info()
    print(f"\n2. VOCABULARIO DISPONIBLE ({vocab_info['total_words']} palabras):")
    for word_type, words in vocab_info['by_type'].items():
        print(f"  {word_type.capitalize()}: {', '.join(words)}")
    
    print(f"\n3. EJEMPLOS DE ANÁLISIS:")
    
    test_sentences = [
        "she eats a cake with a fork",
        "the cat drinks the beer",
        "he cuts meat with a knife",
        "she cooks soup",
        "the dog eats cake",
        "she eats",
        "drinks the cat",
    ]
    
    for sentence_str in test_sentences:
        sentence = sentence_str.split()
        print(f"\n--- Analizando: '{sentence_str}' ---")
        
        is_valid_vocab, invalid_words = analyzer.validate_sentence(sentence)
        if not is_valid_vocab:
            print(f"❌ Vocabulario inválido: {invalid_words}")
            continue
        
        accepted, parse_time, parse_tree = analyzer.parse(sentence)
        
        if accepted:
            print(f"✅ ACEPTADA (Tiempo: {parse_time:.6f}s)")
            
            structure = analyzer.analyze_sentence_structure(sentence)
            print(f"Componentes: {structure.get('components', {})}")
            
            if parse_tree:
                print("Árbol de parsing:")
                analyzer.print_parse_tree(parse_tree, sentence)
                
                try:
                    filename = f"output/parse_trees/demo_english_{'-'.join(sentence)}.json"
                    analyzer.parser.save_parse_tree(parse_tree, filename)
                    print(f"📁 Árbol guardado en: {filename}")
                except Exception as e:
                    print(f"⚠️ Error al guardar árbol: {e}")
        else:
            print(f"❌ RECHAZADA (Tiempo: {parse_time:.6f}s)")
    
    print(f"\n4. PRUEBA COMPREHENSIVA:")
    analyzer.run_comprehensive_test()

def interactive_english_mode():
    print("=== MODO INTERACTIVO: ANALIZADOR DE INGLÉS ===")
    print("Ingrese oraciones en inglés para analizar.")
    print("Escriba 'help' para ver el vocabulario, 'quit' para salir.\n")
    
    analyzer = EnglishGrammarCYK()
    analyzer.convert_to_proper_cnf()
    
    while True:
        try:
            user_input = input("Oración: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'salir']:
                print("¡Hasta luego!")
                break
            
            if user_input.lower() == 'help':
                vocab_info = analyzer.get_vocabulary_info()
                print("\nVOCABULARIO DISPONIBLE:")
                for word_type, words in vocab_info['by_type'].items():
                    print(f"  {word_type.capitalize()}: {', '.join(words)}")
                print()
                continue
            
            if not user_input:
                continue
            
            sentence = user_input.lower().split()
            
            is_valid_vocab, invalid_words = analyzer.validate_sentence(sentence)
            if not is_valid_vocab:
                print(f"❌ Palabras no válidas: {', '.join(invalid_words)}")
                print("Escriba 'help' para ver el vocabulario disponible.\n")
                continue
            
            accepted, parse_time, parse_tree = analyzer.parse(sentence)
            
            if accepted:
                print(f"✅ ORACIÓN VÁLIDA (Tiempo: {parse_time:.6f}s)")
                
                show_details = input("¿Mostrar detalles del análisis? (s/n): ").strip().lower()
                if show_details in ['s', 'si', 'sí', 'y', 'yes']:
                    print("\nTabla CYK:")
                    analyzer.print_table(sentence)
                    
                    if parse_tree:
                        print("\nÁrbol de parsing:")
                        analyzer.print_parse_tree(parse_tree, sentence)
                        
                        try:
                            timestamp = int(time.time())
                            filename = f"output/parse_trees/interactive_{timestamp}_{'-'.join(sentence)}.json"
                            analyzer.parser.save_parse_tree(parse_tree, filename)
                            print(f"📁 Árbol guardado en: {filename}")
                        except Exception as e:
                            print(f"⚠️ Error al guardar árbol: {e}")
                    
                    structure = analyzer.analyze_sentence_structure(sentence)
                    print(f"\nAnálisis estructural:")
                    for key, value in structure.items():
                        if key != 'components':
                            print(f"  {key}: {value}")
            else:
                print(f"❌ ORACIÓN INVÁLIDA (Tiempo: {parse_time:.6f}s)")
                
                show_table = input("¿Mostrar tabla CYK para debugging? (s/n): ").strip().lower()
                if show_table in ['s', 'si', 'sí', 'y', 'yes']:
                    analyzer.print_table(sentence)
            
            print()
            
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_english_mode()
    else:
        demo_english_grammar()