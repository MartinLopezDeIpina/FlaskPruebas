import os
import time

from flask import url_for
from sqlalchemy import text
from treelib import Tree
import csv

from database import db
from models import NodoArbol, RelacionesNodo


def init_routes(app):

    @app.route('/tree')
    def print_tree():
        start = time.time()
        nodos = NodoArbol.query.all()
        relaciones = RelacionesNodo.query.all()

        nodo_dict = {nodo.nodoID: nodo for nodo in nodos}

        tree = Tree()

        tree.create_node(nodos[0].nombre, nodos[0].nodoID)

        for relacion in relaciones:
            ascendente = nodo_dict[relacion.ascendente_id]
            descendente = nodo_dict[relacion.descendente_id]

            tree.create_node(descendente.nombre, descendente.nodoID, parent=ascendente.nodoID)

        print(tree.show(stdout=False))
        tree_str = tree.show(stdout=False)
        #return tree.to_json(with_data=False)
        end = time.time()
        print(f"Time elapsed: {end - start} seconds")
        return tree_str.replace('\n', '<br>')

    @app.route('/tree2')
    def print_tree2():
        root_id = NodoArbol.query.order_by(NodoArbol.nodoID).first()
        sql = text("""
            WITH RECURSIVE tree AS (
            SELECT nodo_arbol.nodoID, nodo_arbol.nombre, NULL::INTEGER as parent_id
            FROM nodo_arbol
            WHERE nodo_arbol.nodoID = :root_id
            
            UNION ALL
            
            SELECT na.nodoID, na.nombre, rn.ascendente_id
            FROM nodo_arbol na
            JOIN relaciones_nodo rn ON na.nodoID = rn.descendente_id
            JOIN tree t ON rn.ascendente_id = t.nodoID
        )
        SELECT * FROM tree;
         
        """)
        result = db.session.execute(sql, {'root_id': root_id}).fetchall()

        # Initialize tree
        tree = Tree()

        # Build tree from result set
        for row in result:
            node_id = row.nodoID
            node_name = row.nombre
            parent_id = row.parent_id

            if parent_id is None:
                tree.create_node(node_name, node_id)  # root node
            else:
                tree.create_node(node_name, node_id, parent=parent_id)

        # Print tree and convert to HTML
        print(tree.show(stdout=False))
        tree_str = tree.show(stdout=False)
        return tree_str.replace('\n', '<br>')

    @app.route('/store')
    def store_skills():
        skills = ['pepe']

        # Create NodoArbol objects for each skill and store them in the database
        for skill in skills:
            nodo = NodoArbol(nombre=skill)
            db.session.add(nodo)

        db.session.commit()

        # Create RelacionesNodo objects to define the relationships between the skills
        # For simplicity, let's assume that each skill is a child of the previous skill
        for i in range(1, len(skills)):
            relacion = RelacionesNodo(ascendente_id=i, descendente_id=i+1)
            db.session.add(relacion)

        # Commit the changes to store the RelacionesNodo objects in the database
        db.session.commit()

    """
    @app.route('/add_csv')
    def store_tree_from_csv():
        file_path = os.path.join(app.static_folder, 'conocimientos.csv')

        # Keep track of the last node at each depth level
        last_node_at_depth = {}

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Iterate over each cell in the row
                for i in range(len(row)):
                    node = row[i]

                    # Skip empty cells
                    if not node:
                        continue

                    parent = last_node_at_depth.get(i - 1)


                    nodo = NodoArbol(nombre=node)
                    #nodo = NodoArbol.query.order_by(-NodoArbol.nombre).first()
                    db.session.add(nodo)
                    db.session.commit()

                    # If the node is not the root node, create a relationship with its parent
                    if parent:
                        relacion = RelacionesNodo(ascendente_id=parent.nodoID, descendente_id=nodo.nodoID)
                        db.session.add(relacion)
                        db.session.commit()

                    # Update the last node at the current depth level
                    last_node_at_depth[i] = nodo
                    """

    @app.route('/delete')
    def delete_tree():
        nodos = NodoArbol.query.all()
        relaciones = RelacionesNodo.query.all()

        for relacion in relaciones:
            db.session.delete(relacion)

        for nodo in nodos:
            db.session.delete(nodo)

        db.session.commit()
        return 'Tree deleted'


    @app.route('/add_csv')
    def store_tree_from_csv():
        file_path = os.path.join(app.static_folder, 'conocimientos.csv')

        # Keep track of the last node at each depth level
        last_node_at_depth = {}

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Iterate over each cell in the row
                for i in range(len(row)):
                    node = row[i]

                    # Skip empty cells
                    if not node:
                        continue

                    parent = last_node_at_depth.get(i - 1)


                    nodo = NodoArbol(nombre=node)
                    db.session.add(nodo)
                    db.session.commit()

                    # If the node is not the root node, create a relationship with its parent
                    if parent:
                        parent_nodo = NodoArbol.query.filter_by(nombre=parent).first()
                        relacion = RelacionesNodo(ascendente_id=parent_nodo.nodoID, descendente_id=nodo.nodoID)
                        db.session.add(relacion)
                        db.session.commit()

                    # Update the last node at the current depth level
                    last_node_at_depth[i] = node
