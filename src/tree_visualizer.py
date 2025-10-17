import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

class TreeVisualizer:
    """
    Clase para visualizar árboles de parsing como imágenes.
    """
    
    def __init__(self):
        self.fig = None
        self.ax = None
        self.node_positions = {}
        self.node_counter = 0
        
    def calculate_tree_layout(self, tree, level=0, position=0, parent_pos=None):
        """
        Calcula las posiciones de todos los nodos en el árbol.
        
        Args:
            tree: Nodo del árbol de parsing
            level (int): Nivel actual en el árbol
            position (int): Posición horizontal
            parent_pos (tuple): Posición del nodo padre
            
        Returns:
            tuple: (nueva_posición, ancho_del_subárbol)
        """
        if tree is None:
            return position, 0
        
        # Calcular posiciones de los hijos primero
        child_positions = []
        current_pos = position
        total_width = 0
        
        if tree.children:
            for child in tree.children:
                child_pos, child_width = self.calculate_tree_layout(
                    child, level + 1, current_pos
                )
                child_positions.append((child_pos, child_width))
                current_pos += max(child_width, 1)
                total_width += max(child_width, 1)
            
            # Posicionar el nodo padre en el centro de sus hijos
            if len(child_positions) > 1:
                first_child_pos = child_positions[0][0]
                last_child_pos = child_positions[-1][0]
                node_x = (first_child_pos + last_child_pos) / 2
            else:
                node_x = child_positions[0][0]
        else:
            # Nodo hoja
            node_x = position
            total_width = 1
        
        # Guardar posición del nodo
        node_y = -level * 2  # Separación vertical entre niveles
        self.node_positions[id(tree)] = (node_x, node_y)
        
        return node_x, max(total_width, 1)
    
    def draw_tree(self, tree, sentence=None, title="Árbol de Parsing", figsize=(12, 8)):
        """
        Dibuja el árbol de parsing.
        
        Args:
            tree: Árbol de parsing a dibujar
            sentence (list): Oración original (opcional)
            title (str): Título del gráfico
            figsize (tuple): Tamaño de la figura
        """
        if tree is None:
            print("No hay árbol para dibujar.")
            return
        
        # Crear figura
        self.fig, self.ax = plt.subplots(1, 1, figsize=figsize)
        self.node_positions = {}
        
        # Calcular layout
        self.calculate_tree_layout(tree)
        
        # Dibujar conexiones (líneas)
        self._draw_edges(tree)
        
        # Dibujar nodos
        self._draw_nodes(tree, sentence)
        
        # Configurar el gráfico
        self.ax.set_aspect('equal')
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Remover ejes
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        
        # Ajustar límites
        if self.node_positions:
            x_coords = [pos[0] for pos in self.node_positions.values()]
            y_coords = [pos[1] for pos in self.node_positions.values()]
            
            margin = 1
            self.ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
            self.ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)
        
        plt.tight_layout()
    
    def _draw_edges(self, tree):
        """
        Dibuja las conexiones entre nodos.
        
        Args:
            tree: Nodo actual del árbol
        """
        if tree is None or not tree.children:
            return
        
        parent_pos = self.node_positions[id(tree)]
        
        for child in tree.children:
            if id(child) in self.node_positions:
                child_pos = self.node_positions[id(child)]
                
                # Dibujar línea
                self.ax.plot(
                    [parent_pos[0], child_pos[0]], 
                    [parent_pos[1], child_pos[1]], 
                    'k-', linewidth=1.5, alpha=0.7
                )
            
            # Recursión
            self._draw_edges(child)
    
    def _draw_nodes(self, tree, sentence=None):
        """
        Dibuja los nodos del árbol.
        
        Args:
            tree: Nodo actual del árbol
            sentence (list): Oración original
        """
        if tree is None:
            return
        
        pos = self.node_positions[id(tree)]
        
        # Determinar color y estilo según el tipo de nodo
        if tree.is_terminal:
            # Nodo terminal (hoja)
            color = '#E8F5E8'
            edge_color = '#4CAF50'
            text_color = '#2E7D32'
            box_style = "round,pad=0.3"
        else:
            # Nodo no terminal
            color = '#E3F2FD'
            edge_color = '#2196F3'
            text_color = '#1565C0'
            box_style = "round,pad=0.3"
        
        # Crear caja para el texto
        bbox = FancyBboxPatch(
            (pos[0] - 0.4, pos[1] - 0.2), 0.8, 0.4,
            boxstyle=box_style,
            facecolor=color,
            edgecolor=edge_color,
            linewidth=1.5
        )
        self.ax.add_patch(bbox)
        
        # Añadir texto
        self.ax.text(
            pos[0], pos[1], tree.symbol,
            ha='center', va='center',
            fontsize=10, fontweight='bold',
            color=text_color
        )
        
        # Si es terminal y tenemos la oración, mostrar la palabra
        if tree.is_terminal and sentence and tree.span:
            word_index = tree.span[0]
            if 0 <= word_index < len(sentence):
                word = sentence[word_index]
                self.ax.text(
                    pos[0], pos[1] - 0.6, f'"{word}"',
                    ha='center', va='center',
                    fontsize=8, style='italic',
                    color='#666666'
                )
        
        # Recursión para hijos
        for child in tree.children:
            self._draw_nodes(child, sentence)
    
    def save_tree_image(self, tree, filename, sentence=None, title="Árbol de Parsing", dpi=300):
        """
        Guarda el árbol como imagen.
        
        Args:
            tree: Árbol de parsing
            filename (str): Nombre del archivo
            sentence (list): Oración original
            title (str): Título del gráfico
            dpi (int): Resolución de la imagen
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Dibujar árbol
            self.draw_tree(tree, sentence, title)
            
            # Guardar imagen
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            
            # Cerrar figura para liberar memoria
            plt.close(self.fig)
            
            print(f"✅ Árbol guardado como imagen: {filename}")
            
        except Exception as e:
            print(f"❌ Error al guardar árbol como imagen: {e}")
    
    def show_tree(self, tree, sentence=None, title="Árbol de Parsing"):
        """
        Muestra el árbol en pantalla.
        
        Args:
            tree: Árbol de parsing
            sentence (list): Oración original
            title (str): Título del gráfico
        """
        self.draw_tree(tree, sentence, title)
        plt.show()
    
    def save_multiple_formats(self, tree, base_filename, sentence=None, title="Árbol de Parsing"):
        """
        Guarda el árbol en múltiples formatos.
        
        Args:
            tree: Árbol de parsing
            base_filename (str): Nombre base del archivo (sin extensión)
            sentence (list): Oración original
            title (str): Título del gráfico
        """
        formats = ['png', 'pdf', 'svg']
        
        for fmt in formats:
            filename = f"{base_filename}.{fmt}"
            try:
                self.draw_tree(tree, sentence, title)
                self.fig.savefig(filename, format=fmt, dpi=300, bbox_inches='tight',
                               facecolor='white', edgecolor='none')
                plt.close(self.fig)
                print(f"✅ Guardado en {fmt.upper()}: {filename}")
            except Exception as e:
                print(f"❌ Error guardando en {fmt.upper()}: {e}")


def create_tree_visualization_methods():
    """
    Funciones para añadir a la clase CYKParser para visualización de árboles.
    """
    
    def save_parse_tree_image(self, tree, filename, sentence=None, title=None):
        """
        Guarda el árbol de parsing como imagen.
        
        Args:
            tree: Árbol de parsing
            filename (str): Nombre del archivo de imagen
            sentence (list): Oración original
            title (str): Título personalizado
        """
        if tree is None:
            print("No hay árbol de parsing para guardar.")
            return
        
        try:
            visualizer = TreeVisualizer()
            
            # Generar título si no se proporciona
            if title is None:
                if sentence:
                    title = f'Árbol de Parsing: "{" ".join(sentence)}"'
                else:
                    title = "Árbol de Parsing"
            
            # Asegurar que el archivo tenga extensión
            if not any(filename.endswith(ext) for ext in ['.png', '.pdf', '.svg', '.jpg']):
                filename += '.png'
            
            visualizer.save_tree_image(tree, filename, sentence, title)
            
        except ImportError:
            print("❌ Error: matplotlib no está instalado.")
            print("Instala con: pip install matplotlib")
        except Exception as e:
            print(f"❌ Error al guardar árbol como imagen: {e}")
    
    def show_parse_tree_image(self, tree, sentence=None, title=None):
        """
        Muestra el árbol de parsing como imagen en pantalla.
        
        Args:
            tree: Árbol de parsing
            sentence (list): Oración original
            title (str): Título personalizado
        """
        if tree is None:
            print("No hay árbol de parsing para mostrar.")
            return
        
        try:
            visualizer = TreeVisualizer()
            
            if title is None:
                if sentence:
                    title = f'Árbol de Parsing: "{" ".join(sentence)}"'
                else:
                    title = "Árbol de Parsing"
            
            visualizer.show_tree(tree, sentence, title)
            
        except ImportError:
            print("❌ Error: matplotlib no está instalado.")
            print("Instala con: pip install matplotlib")
        except Exception as e:
            print(f"❌ Error al mostrar árbol: {e}")
    
    return save_parse_tree_image, show_parse_tree_image


# Ejemplo de uso:
