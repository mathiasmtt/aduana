from app import create_app, db
from app.models import Arancel

def main():
    app = create_app()
    with app.app_context():
        # Buscar productos con "arroz" en la descripción
        arroz_count = Arancel.query.filter(Arancel.DESCRIPCION.ilike('%arroz%')).count()
        print(f"Productos con 'arroz' en la descripción (SQL básico): {arroz_count}")
        
        if arroz_count > 0:
            print("\nPrimeros 5 productos con 'arroz' en la descripción:")
            arroz_products = Arancel.query.filter(Arancel.DESCRIPCION.ilike('%arroz%')).limit(5).all()
            for product in arroz_products:
                print(f"NCM: {product.NCM}, Descripción: {product.DESCRIPCION}")
        
        # Buscar productos que contengan tanto "arroz" como "partido"
        print("\nBúsqueda mejorada: 'arroz partido'")
        arroz_partido = Arancel.buscar_por_descripcion("arroz partido")
        print(f"Productos encontrados: {len(arroz_partido)}")
        for product in arroz_partido:
            print(f"NCM: {product.NCM}, Descripción: {product.DESCRIPCION}")
        
        # Buscar productos que contengan "arroz" y "blanco" en cualquier orden
        print("\nBúsqueda mejorada: 'blanco arroz'")
        blanco_arroz = Arancel.buscar_por_descripcion("blanco arroz")
        print(f"Productos encontrados: {len(blanco_arroz)}")
        for product in blanco_arroz:
            print(f"NCM: {product.NCM}, Descripción: {product.DESCRIPCION}")

if __name__ == "__main__":
    main()
