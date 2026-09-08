# ruff: noqa: E501
"""Case-specific explanations that connect the DEMO to a real development path."""

from __future__ import annotations

CASE_TEACHING = {
    "cash": {
        "mental_model": "El dinero cambia de manos ahora, pero la evidencia digital y el depósito aparecen después.",
        "development_path": [
            "Registrar apertura de caja y responsable.",
            "Emitir recibo por cada recepción.",
            "Cerrar, depositar y conciliar diferencia por turno.",
        ],
        "success_evidence": "Recibo + arqueo + comprobante de depósito asociados a la misma referencia.",
    },
    "paper": {
        "mental_model": "Recibir un cheque no equivale a cobrarlo: existe un período de presentación y posible devolución.",
        "development_path": [
            "Capturar referencia sin almacenar imágenes innecesarias.",
            "Mantener estado pendiente durante clearing.",
            "Aplicar abono o devolución mediante evento bancario.",
        ],
        "success_evidence": "Confirmación del banco y ausencia de devolución dentro de la ventana aplicable.",
    },
    "cards": {
        "mental_model": "La tarjeta autoriza un cargo; captura, liquidación y chargeback son hechos posteriores.",
        "development_path": [
            "Elegir checkout alojado o tokenización.",
            "Crear intent y autenticar cuando corresponda.",
            "Confirmar por webhook, contabilizar y conciliar settlement.",
        ],
        "success_evidence": "ID del proveedor, estado capturado, evento verificado y línea de settlement.",
    },
    "chile-webpay": {
        "mental_model": "Tu web crea una transacción, el cliente paga en Transbank y tu backend confirma el token al retornar.",
        "development_path": [
            "Crear transacción REST en backend.",
            "Redirigir al formulario alojado.",
            "Ejecutar commit una sola vez y consultar ante timeout.",
        ],
        "success_evidence": "Token confirmado por commit/status y conciliado con el reporte del comercio.",
    },
    "chile-oneclick": {
        "mental_model": "Primero se inscribe la tarjeta y luego se cobra usando un token, nunca guardando sus datos completos.",
        "development_path": [
            "Completar start/finish de inscripción.",
            "Cifrar y asociar tbk_user al cliente.",
            "Autorizar con límites, status, refund y baja.",
        ],
        "success_evidence": "Inscripción terminada, autorización por tienda y consentimiento auditables.",
    },
    "chile-khipu": {
        "mental_model": "El cliente autoriza una transferencia en la experiencia bancaria; tu comercio conserva referencia y estado.",
        "development_path": [
            "Crear pago con retorno y notificación.",
            "Abrir la experiencia indicada por Khipu.",
            "Verificar webhook y consultar por payment_id.",
        ],
        "success_evidence": "Payment ID confirmado por API/evento y conciliado con el abono.",
    },
    "mercado-pago": {
        "mental_model": "El frontend obtiene un token o abre un checkout; el access token y la creación viven en backend.",
        "development_path": [
            "Crear aplicación y credenciales de prueba.",
            "Tokenizar/iniciar en frontend sin exponer secreto.",
            "Crear con idempotencia, recibir webhook y consultar.",
        ],
        "success_evidence": "Payment/order ID con estado aprobado, webhook validado y movimiento conciliado.",
    },
    "acceptance-devices": {
        "mental_model": "El dispositivo certificado lee y autentica; la caja coordina el monto y espera el resultado.",
        "development_path": [
            "Contratar/adquirir dispositivo certificado.",
            "Integrar protocolo o SDK sin capturar PIN/PAN.",
            "Cerrar lote y conciliar terminal, adquirente y caja.",
        ],
        "success_evidence": "Voucher, identificador de terminal, autorización y cierre de lote coincidentes.",
    },
    "tokenized-wallets": {
        "mental_model": "La wallet entrega un token de red y un criptograma de esa compra, no el número real de tarjeta.",
        "development_path": [
            "Registrar dominio/app con wallet y PSP.",
            "Validar token/criptograma en backend o PSP.",
            "Procesar y conciliar como tarjeta tokenizada.",
        ],
        "success_evidence": "Token/criptograma aceptado, autorización y referencia de red.",
    },
    "stored-value": {
        "mental_model": "El programa mantiene un saldo propio que debe reservarse y debitarse atómicamente.",
        "development_path": [
            "Modelar cuenta y reglas de expiración.",
            "Reservar saldo con concurrencia segura.",
            "Capturar, liberar o restituir mediante asientos.",
        ],
        "success_evidence": "Saldo anterior + movimientos = saldo nuevo, con journal balanceado.",
    },
    "mobile-money": {
        "mental_model": "El valor vive en una cuenta móvil y entra o sale mediante agentes o bancos.",
        "development_path": [
            "Integrar cuenta/identidad del operador.",
            "Implementar cash-in, pago y cash-out idempotentes.",
            "Conciliar float de agentes y settlement.",
        ],
        "success_evidence": "Referencia del operador y saldos de cliente, agente y tesorería cuadrados.",
    },
    "qr": {
        "mental_model": "El QR transporta datos para iniciar; por sí solo no demuestra que exista pago.",
        "development_path": [
            "Elegir QR estático o dinámico.",
            "Firmar/validar referencia, monto y expiración.",
            "Confirmar por rail y no por la pantalla del pagador.",
        ],
        "success_evidence": "Referencia QR única ligada a confirmación autoritativa.",
    },
    "bank-transfer": {
        "mental_model": "Una instrucción sale de una cuenta y llega a otra; el comprobante visual puede ser falso.",
        "development_path": [
            "Validar beneficiario y referencia.",
            "Iniciar o esperar transferencia por API/banco.",
            "Confirmar por cartola/API y conciliar.",
        ],
        "success_evidence": "Movimiento bancario autoritativo con cuenta, monto, moneda y referencia.",
    },
    "ach": {
        "mental_model": "Las instrucciones viajan por lote y pueden liquidarse o devolverse días después.",
        "development_path": [
            "Generar/validar archivo o usar API del operador.",
            "Controlar ventanas, lotes y totales.",
            "Procesar settlement y returns sin borrar el original.",
        ],
        "success_evidence": "Acuse del lote, settlement y return codes conciliados por entry.",
    },
    "direct-debit": {
        "mental_model": "El comercio cobra porque existe un mandato previo, demostrable y revocable.",
        "development_path": [
            "Capturar consentimiento y versión del mandato.",
            "Presentar débitos con referencia única.",
            "Gestionar rechazos, cancelación y devoluciones.",
        ],
        "success_evidence": "Mandato vigente + presentación aceptada + settlement sin return.",
    },
    "instant-payments": {
        "mental_model": "El rail confirma en segundos, pero tu sistema aún necesita idempotencia y conciliación.",
        "development_path": [
            "Resolver alias/beneficiario.",
            "Enviar instrucción o request-to-pay.",
            "Consumir confirmación final y conciliar en tiempo casi real.",
        ],
        "success_evidence": "ID end-to-end con finalidad confirmada por el rail.",
    },
    "payment-initiation": {
        "mental_model": "Un link o solicitud conecta una orden con una experiencia de pago; no es el rail que liquida.",
        "development_path": [
            "Crear orden con expiración.",
            "Firmar y distribuir URL/QR.",
            "Atribuir el resultado del rail a la orden exacta.",
        ],
        "success_evidence": "Orden, click/iniciación y confirmación unidos por una referencia no reutilizable.",
    },
    "cash-voucher": {
        "mental_model": "Una orden digital se paga físicamente; la confirmación llega después desde la red recaudadora.",
        "development_path": [
            "Emitir barcode/referencia con expiración.",
            "Evitar reutilización y montos ambiguos.",
            "Procesar archivo/evento de recaudación.",
        ],
        "success_evidence": "Referencia pagada en tienda y settlement del recaudador.",
    },
    "credit-alternatives": {
        "mental_model": "Un financiador paga al comercio y el cliente adquiere una obligación en cuotas.",
        "development_path": [
            "Integrar evaluación y consentimiento.",
            "Mostrar costo total y calendario.",
            "Procesar desembolso, cuotas, refund y mora.",
        ],
        "success_evidence": "Contrato aceptado, desembolso al comercio y calendario contable.",
    },
    "carrier-billing": {
        "mental_model": "El operador añade el cargo a la factura o descuenta saldo móvil.",
        "development_path": [
            "Validar número y elegibilidad.",
            "Obtener consentimiento/OTP y aplicar límites.",
            "Recibir resultado y conciliar settlement del operador.",
        ],
        "success_evidence": "Consentimiento, transaction ID y reporte del operador.",
    },
    "platform-payments": {
        "mental_model": "Un cobro bruto se divide entre comercio, plataforma, reserva y futuros payouts.",
        "development_path": [
            "Completar KYB/onboarding de participantes.",
            "Definir split inmutable por orden.",
            "Mantener subledger y ejecutar payouts conciliados.",
        ],
        "success_evidence": "Bruto = netos + comisión + reserva, y cada payout tiene trazabilidad.",
    },
    "b2b": {
        "mental_model": "La factura necesita aprobación, instrucción bancaria y aplicación contable en ERP.",
        "development_path": [
            "Ingerir y validar factura.",
            "Modelar segregación de funciones/aprobaciones.",
            "Enviar pago y aplicar remittance al ERP.",
        ],
        "success_evidence": "Factura aprobada, instrucción bancaria y asiento ERP con la misma referencia.",
    },
    "international": {
        "mental_model": "El valor cruza monedas y entidades; fees, FX, sanciones y fecha valor cambian el resultado.",
        "development_path": [
            "Cotizar FX y mostrar fees.",
            "Realizar screening y recopilar propósito.",
            "Rastrear corresponsales, settlement y monto recibido.",
        ],
        "success_evidence": "Referencia end-to-end, tasa/fees aceptados y confirmación del beneficiario.",
    },
    "high-value": {
        "mental_model": "RTGS prioriza finalidad y liquidez; una operación puede esperar en cola.",
        "development_path": [
            "Integrar mensajería/canal autorizado.",
            "Controlar aprobación dual, prioridad y liquidez.",
            "Registrar aceptación final y conciliación intradía.",
        ],
        "success_evidence": "Mensaje aceptado por el sistema RTGS con finalidad y timestamp.",
    },
    "open-finance": {
        "mental_model": "Una aplicación inicia desde la cuenta solo dentro del consentimiento y alcance otorgados.",
        "development_path": [
            "Registrar TPP/cliente según regulación.",
            "Implementar FAPI, PKCE y consentimiento.",
            "Usar token ligado, iniciar y consultar el pago.",
        ],
        "success_evidence": "Consent ID, token con alcance mínimo y payment ID confirmado.",
    },
    "digital-assets": {
        "mental_model": "Una firma autoriza transferencia del activo; confirmación y custodia definen el riesgo real.",
        "development_path": [
            "Decidir custodia y red.",
            "Crear address/invoice y política de fees.",
            "Observar mempool/confirmaciones o settlement Lightning.",
        ],
        "success_evidence": "Transaction ID o payment hash validado y conciliado con la orden.",
    },
    "machine-payments": {
        "mental_model": "Una máquina paga dentro de una política; no recibe autoridad ilimitada.",
        "development_path": [
            "Identificar dispositivo y medidor.",
            "Emitir credencial limitada por monto/uso/tiempo.",
            "Autorizar, registrar consumo y conciliar.",
        ],
        "success_evidence": "Identidad, medición, decisión de política y settlement unidos.",
    },
    "agentic-payments": {
        "mental_model": "El agente propone o ejecuta dentro de un mandato verificable y límites humanos.",
        "development_path": [
            "Definir mandato, presupuesto y comercios permitidos.",
            "Exigir aprobación humana por riesgo.",
            "Usar credencial de alcance mínimo y audit trail.",
        ],
        "success_evidence": "Mandato + decisión + aprobación + referencia del pago reproducibles.",
    },
}


def teaching_for(rail_id: str) -> dict[str, object]:
    try:
        teaching = CASE_TEACHING[rail_id]
    except KeyError as exc:
        raise ValueError(f"missing teaching guide for {rail_id}") from exc
    return {
        "mental_model": str(teaching["mental_model"]),
        "development_path": list(teaching["development_path"]),
        "success_evidence": str(teaching["success_evidence"]),
    }
