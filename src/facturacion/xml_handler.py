import xml.etree.ElementTree as ET
from decimal import Decimal
from servicios.models import FacturaServicio
from gastos.models import FacturaGasto, LineaDetalleGasto, ImpuestoDetalleGasto
from django.db import transaction

class Facturas:
    errors = []

    def __init__(self, xml_file, user, tipo):
        self.xml_file = xml_file
        self.user = user
        self.tipo = tipo
        self.errors = []

    def validar(self):
        if not self.xml_file.name.endswith('.xml'):
            self.errors.append('Error, Tipo de documento no válido')
            return False
        return True
    
    def _xml_to_dict(self, element):
        """
        Convierte recursivamente un elemento XML en un diccionario.
        """
        result = {}

        for child in element:
            tag_name = child.tag.split('}')[-1]  # Eliminar namespace del tag
            text = child.text.strip() if child.text else None  # Limpiar espacios en texto

            # Si el hijo tiene más subelementos, hacer recursión
            if len(child):
                value = self._xml_to_dict(child)
            else:
                value = text

            # Si hay múltiples elementos con el mismo nombre, hacer una lista
            if tag_name in result:
                if isinstance(result[tag_name], list):
                    result[tag_name].append(value)
                else:
                    result[tag_name] = [result[tag_name], value]
            else:
                result[tag_name] = value

        return result
    
    def toDict(self, root, tag, ns):
        """
        Convierte un elemento XML en un diccionario.
        """
        element = root.find(tag, ns)
        return self._xml_to_dict(element) if element is not None else {}
    

    def handle_uploaded_file(self):
        ns = {'def': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica'}

        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()

            if root.tag.endswith('FacturaElectronica'):
                # Extraer datos directamente, ya que siempre estarán presentes
                clave = root.find("def:Clave", ns).text 
                codigo_actividad = root.find("def:CodigoActividad", ns).text
                numero_consecutivo = root.find("def:NumeroConsecutivo", ns).text
                
                receptor = self.toDict(root, "def:Receptor", ns)
                emisor = self.toDict(root, "def:Emisor", ns)
                resumen_fact = self.toDict(root, "def:ResumenFactura", ns)

                # Extraer datos obligatorios
                emisor_identificacion = emisor['Identificacion']['Numero']
                receptor_identificacion = receptor['Identificacion']['Numero']
                codigo_moneda = resumen_fact['CodigoTipoMoneda']['CodigoMoneda']
                tipo_cambio = Decimal(resumen_fact['CodigoTipoMoneda']['TipoCambio'])

                # Condición 1: Verificar si la identificación del emisor coincide con la del usuario para la carga de facturas de servicios
                if emisor_identificacion != self.user.num_identificacion and self.tipo == 'servicio':
                    self.errors.append("Error, la identificación del comprobante no coincide con la del usuario")
                    return
                
                # Condición 2: Verificar si la identificación del receptor coincide con la del usuario para la carga de facturas de compras
                if receptor_identificacion != self.user.num_identificacion and self.tipo == 'compra':
                    self.errors.append("Error, la identificación del receptor no coincide con la del usuario")
                    return


                # Condición 3: Verificar si la clave de la factura ya está registrada
                if FacturaServicio.objects.filter(clave=clave).exists() or FacturaGasto.objects.filter(clave=clave).exists():
                    self.errors.append("Error, la factura ya está registrada")
                    return

                if self.tipo == 'servicio':
                    # Crear una instancia del modelo FacturaServicio
                    factura_servicio = FacturaServicio(
                        clave = clave,
                        codigo_actividad = codigo_actividad,
                        numero_consecutivo = numero_consecutivo,
                        fecha_emision=root.find("def:FechaEmision", ns).text,
                        emisor_nombre=emisor.get('Nombre'),
                        emisor_identificacion=emisor_identificacion,
                        receptor_nombre=receptor.get('Nombre'),
                        receptor_identificacion=receptor_identificacion,
                        total_gravado=Decimal(resumen_fact.get('TotalGravado')) if codigo_moneda == 'CRC' else Decimal(resumen_fact.get('TotalGravado')) * tipo_cambio,
                        total_impuesto=Decimal(resumen_fact.get('TotalImpuesto')) if codigo_moneda == 'CRC' else Decimal(resumen_fact.get('TotalImpuesto')) * tipo_cambio,
                        total_comprobante=Decimal(resumen_fact.get('TotalComprobante')) if codigo_moneda == 'CRC' else Decimal(resumen_fact.get('TotalComprobante')) * tipo_cambio
                    )

                    # Guardar la instancia en la base de datos
                    factura_servicio.save()

                elif self.tipo == 'compra':
                    # Crear una instancia del modelo LineaDetalleGasto
                    with transaction.atomic():
                        factura_gasto = FacturaGasto(
                            clave = clave,
                            codigo_actividad = codigo_actividad,
                            numero_consecutivo = numero_consecutivo,
                            fecha_emision=root.find("def:FechaEmision", ns).text,
                            emisor_nombre=emisor.get('Nombre'),
                            emisor_identificacion=emisor_identificacion,
                            receptor_nombre=receptor.get('Nombre'),
                            receptor_identificacion=receptor_identificacion,
                            total_venta_neta=Decimal(resumen_fact.get('TotalVentaNeta')) if codigo_moneda == 'CRC' else Decimal(resumen_fact.get('TotalVentaNeta')) * tipo_cambio,
                            total_impuesto=Decimal(resumen_fact.get('TotalImpuesto')) if codigo_moneda == 'CRC' else Decimal(resumen_fact.get('TotalImpuesto')) * tipo_cambio,
                            total_comprobante=Decimal(resumen_fact.get('TotalComprobante')) if codigo_moneda == 'CRC' else Decimal(resumen_fact.get('TotalComprobante')) * tipo_cambio
                        )

                        # Guardar la instancia en la base de datos
                        factura_gasto.save()

                    # Procesar líneas de detalle
                    detalle_servicio = root.find("def:DetalleServicio", ns)
                    for linea_xml in detalle_servicio.findall("def:LineaDetalle", ns):
                        self.procesar_linea_detalle(linea_xml, factura_gasto, ns, codigo_moneda, tipo_cambio)
 
            #if not self.errors:
                #self.errors.append("Factura y detalles cargados correctamente")

        except ET.ParseError:
            self.errors.append("Error al analizar el XML")
        except KeyError as e:
            self.errors.append("Falta el campo obligatorio en el XML: "+str(e))
        except Exception as e:
            self.errors.append("Error inesperado: "+str(e)) 
            print(e)

    def procesar_linea_detalle(self, linea_xml, factura, ns, codigo_moneda, tipo_cambio):
        # Extraer datos básicos de la línea
        linea_data = {
            'numero_linea': int(linea_xml.find("def:NumeroLinea", ns).text),
            'codigo': linea_xml.findtext("def:Codigo", "", ns).strip(),
            'nombre': linea_xml.findtext("def:Detalle", "", ns).strip(),
            'cantidad': Decimal(linea_xml.find("def:Cantidad", ns).text),
            'unidad_medida': linea_xml.findtext("def:UnidadMedida", "Unid", ns).strip(),
            'precio_unitario': Decimal(linea_xml.find("def:PrecioUnitario", ns).text) if codigo_moneda == 'CRC' else Decimal(linea_xml.find("def:PrecioUnitario", ns).text) * tipo_cambio,
            'monto_total': Decimal(linea_xml.find("def:MontoTotal", ns).text) if codigo_moneda == 'CRC' else Decimal(linea_xml.find("def:MontoTotal", ns).text) * tipo_cambio,
            'descuento': self.obtener_descuento(linea_xml, ns) if codigo_moneda == 'CRC' else self.obtener_descuento(linea_xml, ns) * tipo_cambio,
            'monto_total_linea': Decimal(linea_xml.find("def:MontoTotalLinea", ns).text) if codigo_moneda == 'CRC' else Decimal(linea_xml.find("def:MontoTotalLinea", ns).text) * tipo_cambio,
            'tipo_compra': self.determinar_tipo_compra(linea_xml, ns)
        }

        # Crear línea de detalle
        linea = LineaDetalleGasto(factura_gasto=factura, **linea_data)
        linea.save()

        # Procesar impuestos de la línea
        for impuesto_xml in linea_xml.findall("def:Impuesto", ns):
            self.procesar_impuesto(impuesto_xml, linea, ns, codigo_moneda, tipo_cambio)

    def obtener_descuento(self, linea_xml, ns):
        descuento = linea_xml.find("def:Descuento", ns)
        if descuento is not None:
            return Decimal(descuento.find("def:MontoDescuento", ns).text)
        return Decimal('0.00')

    def determinar_tipo_compra(self, linea_xml, ns):
        """
        Determina el tipo de compra basado en los impuestos de la línea de detalle.
        
        Args:
            linea_xml (Element): El elemento XML que contiene la información de la línea de detalle.
            ns (dict): El diccionario de namespaces para buscar elementos en el XML.
        
        Returns:
            str: El tipo de compra ('exento', 'con_iva', 'no_acreditable', 'sin_iva').
        """
            # Lógica de determinación de tipo de compra
        for impuesto in linea_xml.findall("def:Impuesto", ns):
            codigo = impuesto.findtext("def:Codigo", "", ns)
            codigo_tarifa = impuesto.findtext("def:CodigoTarifa", "", ns)
            
            if codigo == '01':  # IVA
                if codigo_tarifa == '01':
                    return 'exento'
                elif codigo_tarifa == '08':
                    return 'con_iva'
                else:
                    return 'no_acreditable'
        return 'sin_iva'

    def procesar_impuesto(self, impuesto_xml, linea, ns, codigo_moneda, tipo_cambio):
        # Extraer datos del impuesto
        impuesto_data = {
            'codigo': impuesto_xml.findtext("def:Codigo", "", ns),
            'codigo_tarifa': impuesto_xml.findtext("def:CodigoTarifa", "", ns),
            'tarifa': Decimal(impuesto_xml.find("def:Tarifa", ns).text),
            'monto': Decimal(impuesto_xml.find("def:Monto", ns).text) if codigo_moneda == 'CRC' else Decimal(impuesto_xml.find("def:Monto", ns).text) * tipo_cambio
        }

        # Crear registro de impuesto
        impuesto = ImpuestoDetalleGasto(linea_detalle=linea, **impuesto_data)
        impuesto.save()