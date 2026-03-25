from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ==================== ERP ====================

class ERP(db.Model):
    __tablename__ = 'erps'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    descripcion = db.Column(db.String(500))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    color_primario = db.Column(db.String(7), default='#667eea')  # Color del sidebar
    icono = db.Column(db.String(50), default='📊')  # Emoji representativo
    
    def __repr__(self):
        return f'<ERP {self.nombre}>'

# ==================== USUARIO ====================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    nombre = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255))
    rol = db.Column(db.String(50), default='usuario')  # admin, usuario
    permisos = db.Column(db.String(50), default='view')  # view, edit
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    idioma = db.Column(db.String(10), default='es')  # es, en
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

# ==================== MAESTROS ====================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    cuit = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(255))
    saldo = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True, cascade="all, delete-orphan")
    cobranzas = db.relationship('Cobranza', backref='cliente', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'


class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    cuit = db.Column(db.String(20), unique=True)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(255))
    saldo = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    productos = db.relationship('Producto', backref='proveedor', lazy=True, cascade="all, delete-orphan")
    pagos = db.relationship('Pago', backref='proveedor', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'


class ProveedorLogistico(db.Model):
    __tablename__ = 'proveedores_logisticos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(255))
    tarifa = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    pedidos = db.relationship('Pedido', backref='prov_logistico', lazy=True)
    
    def __repr__(self):
        return f'<ProveedorLogistico {self.nombre}>'


class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    clasificacion = db.Column(db.String(100))
    variedad = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    envase = db.Column(db.String(100))
    costo_unitario = db.Column(db.Float, default=0)
    stock = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    items_pedido = db.relationship('ItemPedido', backref='producto', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'


# ==================== COTIZACIONES ====================

class Cotizacion(db.Model):
    __tablename__ = 'cotizaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False)
    margen_ganancia = db.Column(db.Float, default=30)  # porcentaje por defecto 30%
    precio_venta = db.Column(db.Float)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    producto = db.relationship('Producto', backref='cotizaciones', lazy=True)
    
    def calcular_precio_venta(self):
        """Calcula el precio de venta basado en costo y margen"""
        if self.margen_ganancia is None:
            self.margen_ganancia = 30
        self.precio_venta = self.costo_unitario * (1 + self.margen_ganancia / 100)
        return self.precio_venta
    
    def __repr__(self):
        return f'<Cotizacion {self.producto.nombre if self.producto else "?"} {self.fecha_desde}>'


class ConfigMargen(db.Model):
    """Configuración global de margen por defecto"""
    __tablename__ = 'config_margen'
    
    id = db.Column(db.Integer, primary_key=True)
    margen_default = db.Column(db.Float, default=30)  # 30% por defecto
    
    def __repr__(self):
        return f'<ConfigMargen {self.margen_default}%>'


# ==================== TRANSACCIONALES ====================

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    prov_logistico_id = db.Column(db.Integer, db.ForeignKey('proveedores_logisticos.id'))
    fecha_venta = db.Column(db.DateTime, default=datetime.now)
    fecha_carga = db.Column(db.DateTime)
    mercado = db.Column(db.String(100))
    puesto = db.Column(db.String(50))
    remito = db.Column(db.String(50))
    cargado = db.Column(db.Boolean, default=False)
    entregado = db.Column(db.Boolean, default=False)
    
    # Montos
    costo_total = db.Column(db.Float, default=0)
    precio_venta_total = db.Column(db.Float, default=0)
    comision = db.Column(db.Float, default=0)
    resultado = db.Column(db.Float, default=0)
    
    # Relaciones
    items = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Pedido {self.numero}>'


class ItemPedido(db.Model):
    __tablename__ = 'items_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(50), default='Pallets')
    precio_unitario = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<ItemPedido {self.id}>'


class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.now)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(100))
    referencia = db.Column(db.String(100))
    notas = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Pago {self.id}>'


class Cobranza(db.Model):
    __tablename__ = 'cobranzas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha_cobranza = db.Column(db.DateTime, default=datetime.now)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(100))
    referencia = db.Column(db.String(100))
    notas = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Cobranza {self.id}>'
