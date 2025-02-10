from app import app, db
from models.carga import Carga
from models.logistica import Logistica
from models.gerencia import Gerencia

def verificar_carga_por_numero(numero_carga):
    with app.app_context():
        carga = db.session.query(Carga).filter_by(carga=str(numero_carga)).first()
        if not carga:
            print(f"Carga número {numero_carga} não encontrada")
            return
        mostrar_valores(carga)

def verificar_carga_por_id(carga_id):
    with app.app_context():
        carga = db.session.get(Carga, carga_id)
        if not carga:
            print(f"Carga ID {carga_id} não encontrada")
            return
        mostrar_valores(carga)

def mostrar_valores(carga):
    # Valores do controle de frete
    valor_frete = carga.controle_frete.valor_frete if carga.controle_frete else 0
    entrega_extra = carga.controle_frete.entrega_extra if carga.controle_frete else 0
    
    # Valores da logística e gerência
    diarias = carga.gerencia.diarias if carga.gerencia else 0
    descarga = carga.logistica.descarga if carga.logistica else 0
    
    # Peso total dos romaneios
    peso_total = sum(romaneio.peso_bruto for romaneio in carga.romaneios) if carga.romaneios else 0
    
    print(f"\nValores da carga {carga.carga} (ID: {carga.id}):")
    print(f"Valor frete: R$ {valor_frete:.2f}")
    print(f"Entrega extra: R$ {entrega_extra:.2f}")
    print(f"Diárias: R$ {diarias:.2f}")
    print(f"Descarga: R$ {descarga:.2f}")
    print(f"Peso total: {peso_total:.2f} kg")
    
    if peso_total > 0:
        valor_total = valor_frete + entrega_extra + diarias + descarga
        preco_kg = valor_total / peso_total
        print(f"\nCálculo:")
        print(f"Valor total: R$ {valor_total:.2f}")
        print(f"Preço por kg: R$ {preco_kg:.2f}")
        print(f"Fórmula: ({valor_frete:.2f} + {entrega_extra:.2f} + {diarias:.2f} + {descarga:.2f}) / {peso_total:.2f}")

if __name__ == "__main__":
    print("Buscando por número da carga:")
    verificar_carga_por_numero("5173")
