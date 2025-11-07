# Asegúrate de importar todas las dependencias necesarias dentro de este archivo
from datetime import datetime
import re
import os

from api_clients.trello_client import TrelloClient
from api_clients.jira_client import JiraClient
import utils.config as config
from utils.config import FRAMEWORK_LOGGER as logger
from .test_helpers import _buscar_evidencias_por_nombre_test, _obtener_video_evidencia

# ----------------------------------------------------------------------------------
# REPORTE A TRELLO
# ----------------------------------------------------------------------------------

def _handle_trello_reporting(item, report):
    """
    Función auxiliar dedicada a gestionar la creación, actualización y
    movimiento de tarjetas en Trello para reportar fallos y cierres exitosos.

    :param item: Objeto de elemento de prueba de Pytest.
    :param report: Objeto de reporte de la fase 'teardown'.
    """
    
    # -----------------------------------------------------------------------------------
    # 1. LÓGICA DE FALLO (Reporte y manejo de re-fallo)
    # -----------------------------------------------------------------------------------
    if report.when == "teardown" and hasattr(item, '_failed_report'):
        logger.info(f"\n[TRELLO-HANDLER] Procesando reporte de FALLO en Teardown para: {item.name}")
        
        try:
            # 1.1. Inicialización y Extracción de Datos Críticos
            trello_client = TrelloClient()
            ambiente_actual = getattr(config, 'AMBIENTE', 'N/A').upper()
            test_name_full = item.name
            
            # Obtener IDs y pasos
            test_id_match = re.search(r'\[ID:\s*(.+?)\]', item.obj.__doc__ or '')
            test_case_id = test_id_match.group(1) if test_id_match else 'N/A'
            navegador_dispositivo_id = item.callspec.id if hasattr(item, 'callspec') and hasattr(item.callspec, 'id') else 'N/A'
            test_name_clean = re.sub(r'\[.*?\]$', '', item.name).strip()
            test_steps_list = getattr(item, '_test_steps_result', [])
            
            # 1.2. Lógica de Deduplicación y Re-Fallo (BUSCAR)
            existing_card_data = trello_client.find_card_by_test_id(
                test_case_id, ambiente_actual, navegador_dispositivo_id
            )
            existing_card_id = existing_card_data.get('id') if existing_card_data else None
            
            # Construcción de la descripción (omitiendo por brevedad, el original es correcto)
            card_details = "..." # Lógica de construcción de card_details del código original
            
            # (El resto del código de construcción de card_details del código original...)
            card_details = "### Detalles de la Falla\n\n" 
            card_details += f"**ID del Test:** {test_case_id}\n"
            card_details += f"**ID de la prueba:** `{report.nodeid}`\n"
            card_details += f"**Ambiente:** {ambiente_actual}\n" 
            card_details += f"**Navegador/Dispositivo:** `{navegador_dispositivo_id}`\n" 
            card_details += "### Pasos del Test Ejecutados\n\n"
            if test_steps_list:
                for paso_con_timestamp in test_steps_list:
                    card_details += f"➡️ {paso_con_timestamp}\n" 
                card_details += f"\n❌ **[FALLO DE ASERCIÓN EN ESTE PUNTO]** Ver traza de error/evidencias adjuntas.\n"
            else:
                card_details += "No se registraron pasos de prueba.\n"
                
            card_details += f"**### Resumen de la Falla:**\n```python\n{item._failed_report.longreprtext}\n```\n\n"
            card_details += f"\n---\nReporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            card_id = None
            if existing_card_id:
                # Caso RE-FALLO
                comment = f"⚠️ RE-FALLO DETECTADO ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) en ambiente {ambiente_actual} / {navegador_dispositivo_id}:\n\n{card_details}"
                trello_client.add_comment_to_card(existing_card_id, comment)
                card_id = existing_card_id

                current_list_name = existing_card_data.get('list_name')
                if current_list_name in ['QA', 'ONGOING']:
                    trello_client.move_card(card_id, 'FAIL') # El log de éxito/fallo está dentro del cliente
            else:
                # Caso NUEVO FALLO
                card_title = (
                    f"🔴 FALLO: {ambiente_actual} - ({test_case_id}) " 
                    f"[{navegador_dispositivo_id}] - {test_name_clean} - ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                )
                card_response = trello_client.create_card(card_title, card_details)
                card_id = card_response.get('id') if card_response else None

            # 1.3. Adjuntar evidencias
            if card_id:
                evidencias = _buscar_evidencias_por_nombre_test(test_name_full)
                archivos_adjuntados = 0
                for file_path in evidencias:
                    if trello_client.attach_file_to_card(card_id, file_path):
                        archivos_adjuntados += 1
                logger.info(f"\n✅ Proceso de reporte a Trello finalizado. {archivos_adjuntados} archivos adjuntados.")
            else:
                logger.warning("\n⚠️ Advertencia: No se pudo obtener el ID de la tarjeta Trello. No se adjuntarán evidencias.")

        except Exception as e:
            logger.critical(f"\n❌ ERROR CRÍTICO: Fallo al procesar el reporte Trello para '{item.nodeid}'. Fallo: {e}", exc_info=True)
            
        # Limpiar el estado de fallo
        del item._failed_report

    # -----------------------------------------------------------------------------------
    # 2. LÓGICA DE ÉXITO (Mover a DONE)
    # -----------------------------------------------------------------------------------
    elif report.passed and report.when == "teardown" and not hasattr(item, '_failed_report'):
        logger.info(f"\n[TRELLO-HANDLER] Procesando reporte de ÉXITO en Teardown para: {item.name}")
        
        try:
            trello_client = TrelloClient()
            ambiente_actual = getattr(config, 'AMBIENTE', 'N/A').upper()
            navegador_dispositivo_id = item.callspec.id if hasattr(item, 'callspec') and hasattr(item.callspec, 'id') else 'N/A'
            test_id_match = re.search(r'\[ID:\s*(.+?)\]', item.obj.__doc__ or '')
            test_case_id = test_id_match.group(1) if test_id_match else 'N/A'
            test_steps_list = getattr(item, '_test_steps_result', [])

            # Buscar tarjeta existente (solo si se necesita cerrar una previa)
            existing_card_data = trello_client.find_card_by_test_id(
                test_case_id, ambiente_actual, navegador_dispositivo_id
            )
            card_id = existing_card_data.get('id') if existing_card_data else None 
            video_path = _obtener_video_evidencia(item.name) 
            
            if card_id:
                # Adjuntar Video y preparar el comentario
                video_info_comment = ""
                if video_path:
                    video_filename = os.path.basename(video_path)
                    trello_client.attach_video_to_card(card_id, video_path)
                    video_info_comment = f"\n🎥 **Evidencia de video adjunta:** `{video_filename}`."
                
                # Preparar pasos exitosos (omitiendo por brevedad)
                steps_details = "..." # Lógica de pasos del código original

                steps_details = "### Pasos del Test Ejecutados\n\n"
                if test_steps_list:
                    for paso_con_timestamp in test_steps_list:
                        steps_details += f"✅ {paso_con_timestamp}\n"
                    steps_details += f"\n---"
                else:
                    steps_details += "No se registraron pasos de prueba.\n\n---"
                
                # Añadir comentario y mover a DONE
                success_comment = (
                    f"✅ PRUEBA REPARADA/EXITOSA ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).\n\n"
                    f"**ID del Test:** {test_case_id}\n"
                    f"{video_info_comment}\n\n"
                    f"{steps_details}\n"
                    f"\n**Movido a DONE.**"
                )
                trello_client.add_comment_to_card(card_id, success_comment)
                trello_client.move_card(card_id, 'DONE')
                
            else:
                logger.debug(f"\n[TRELLO-HANDLER] No se encontró tarjeta para cerrar ({test_case_id}).")
                
        except Exception as e:
            logger.error(f"\n❌ Error al procesar el cierre de tarjeta Trello para la prueba exitosa '{item.nodeid}'. Fallo: {e}", exc_info=False)

# ----------------------------------------------------------------------------------
# REPORTE A JIRA
# ----------------------------------------------------------------------------------
def _handle_jira_reporting(item, report):
    """
    Función auxiliar dedicada a gestionar la creación, actualización y
    transición de Issues en Jira para reportar fallos y cierres exitosos.

    :param item: Objeto de elemento de prueba de Pytest.
    :param report: Objeto de reporte de la fase 'teardown'.
    """
    ambiente_actual = getattr(config, 'AMBIENTE', 'N/A').upper()

    # Extracción de IDs comunes a Trello y Jira
    test_id_match = re.search(r'\[ID:\s*(.+?)\]', item.obj.__doc__ or '')
    test_case_id = test_id_match.group(1) if test_id_match else 'N/A'
    navegador_dispositivo_id = item.callspec.id if hasattr(item, 'callspec') and hasattr(item.callspec, 'id') else 'N/A'
    test_name_clean = re.sub(r'\[.*?\]$', '', item.name).strip()
    test_name_full = item.name
    test_steps_list = getattr(item, '_test_steps_result', [])

    # -----------------------------------------------------------------------------------
    # 1. LÓGICA DE FALLO (Reporte y manejo de re-fallo)
    # -----------------------------------------------------------------------------------
    if report.when == "teardown" and hasattr(item, '_failed_report'):
        logger.info(f"\n[JIRA-HANDLER] Procesando reporte de FALLO en Teardown para: {item.name}")

        try:
            jira_client = JiraClient()
            
            # 1.1. Lógica de Deduplicación (BUSCAR)
            # El Issue debe tener un ID/Key y un estado para ser reportable.
            existing_issue_data = jira_client.find_issue_by_test_id(
                test_case_id, ambiente_actual, navegador_dispositivo_id
            )
            existing_issue_key = existing_issue_data.get('key') if existing_issue_data else None

            # 1.2. Construcción de la Descripción (similar a la lógica de Trello)
            # Jira utiliza un formato de texto enriquecido (ADF) pero el API acepta
            # texto plano que convertiremos a ADF simple.
            issue_description = "### Detalles de la Falla\n\n"
            issue_description += f"**ID del Test:** {test_case_id}\n"
            issue_description += f"**ID de la prueba:** {report.nodeid}\n"
            issue_description += f"**Ambiente:** {ambiente_actual}\n"
            issue_description += f"**Navegador/Dispositivo:** {navegador_dispositivo_id}\n"
            issue_description += "### Pasos del Test Ejecutados\n\n"

            if test_steps_list:
                for paso_con_timestamp in test_steps_list:
                    issue_description += f"➡️ {paso_con_timestamp}\n"
                issue_description += f"\n❌ **[FALLO DE ASERCIÓN EN ESTE PUNTO]** Ver traza de error/evidencias adjuntas.\n"
            else:
                issue_description += "No se registraron pasos de prueba.\n"

            issue_description += f"**### Resumen de la Falla:**\n{{code:python}}\n{item._failed_report.longreprtext}\n{{code}}\n\n" # Formato code block en Jira
            issue_description += f"\n---\nReporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            if existing_issue_key:
                # Caso RE-FALLO (Issue Abierto)
                logger.warning(f"\n⚠️ RE-FALLO DETECTADO. Issue: {existing_issue_key}. Añadiendo comentario.")

                # 1. Preparación del COMENTARIO (Incluyendo Pasos del Test)
                comment = (
                    f"⚠️ RE-FALLO DETECTADO ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) en ambiente {ambiente_actual} / {navegador_dispositivo_id}.\n\n"
                )

                # Añadir los pasos ejecutados al cuerpo del comentario
                comment += "### Pasos del Test Ejecutados en este Re-fallo\n\n"

                if test_steps_list:
                    for paso_con_timestamp in test_steps_list:
                        comment += f"➡️ {paso_con_timestamp}\n"
                    comment += f"\n❌ **[FALLO DE ASERCIÓN EN ESTE PUNTO]** Ver traza de error/evidencias adjuntas.\n"
                else:
                    comment += "No se registraron pasos de prueba.\n"

                # 2. Añadir el resumen de la falla
                comment += (
                    f"### Resumen de la Falla:\n{{code:python}}\n{item._failed_report.longreprtext}\n{{code}}\n\n"
                    f"--- Ver descripción original para detalles del test ---\n"
                )
                
                # 3. Añadir el comentario al Issue
                jira_client.add_comment_to_issue(existing_issue_key, comment)

                # 4. Lógica de transición (Mantenemos la corrección de 'Por hacer')
                current_status = existing_issue_data.get('status', '').lower()

                if current_status not in ['por hacer', 'to do']:
                    jira_client.transition_issue(existing_issue_key, 'por hacer')
                    logger.info(f"\n🔄 Issue {existing_issue_key} movido a POR HACER (Reabierto).")

                issue_key = existing_issue_key

                # 5. Lógica de Adjuntos (Añadida en el paso anterior)
                logger.info(f"\n📎 Adjuntando nuevas evidencias de re-fallo al Issue existente: {existing_issue_key}.")
                archivos_adjuntados = 0
                evidencias = _buscar_evidencias_por_nombre_test(test_name_full)

                for file_path in evidencias:
                    if jira_client.attach_file_to_issue(issue_key, file_path):
                        archivos_adjuntados += 1
                       
                logger.info(f"\n✅ Proceso de re-reporte a Jira finalizado. {archivos_adjuntados} nuevos archivos adjuntados al Issue: {issue_key}.")
                
            else:
                # Caso NUEVO FALLO (Crear Issue)
                issue_summary = (
                    f"🔴 FALLO: {ambiente_actual} - ({test_case_id}) "
                    f"[{navegador_dispositivo_id}] - {test_name_clean}"
                )

                # Suponemos que create_issue retorna la key del Issue o None/Falsy
                issue_key = jira_client.create_issue(issue_summary, issue_description)

                if issue_key:
                    logger.info(f"\n✅ Issue Jira creado: '{issue_key}' (Proyecto: {jira_client.project_key}).")

                    # 1.3. Adjuntar evidencias (Screenshots, Video, Traceview)
                    archivos_adjuntados = 0
                    evidencias = _buscar_evidencias_por_nombre_test(test_name_full)

                    # Nota: El nombre de tu función era `attach_file_to_issue` en tu código.
                    for file_path in evidencias:
                        if jira_client.attach_file_to_issue(issue_key, file_path):
                            archivos_adjuntados += 1

                    # Esto asegura la visibilidad en el tablero.
                    logger.info(f"\n🔄 Transicionando nuevo Issue {issue_key} a estado 'POR HACER' para visibilidad en tablero.")
                    jira_client.transition_issue(issue_key, 'POR HACER')
                    logger.info(f"\n✅ Proceso de reporte a Jira finalizado. {archivos_adjuntados} archivos adjuntados al Issue: {issue_key}.")
                else:
                    logger.warning("\n⚠️ Advertencia: Fallo al crear el Issue en Jira. No se adjuntarán evidencias.")

        except Exception as e:
            logger.critical(f"\n❌ ERROR CRÍTICO: Fallo al procesar el reporte Jira para '{item.nodeid}'. Fallo: {e}", exc_info=True)

        # Limpiar el estado de fallo del item (esto es importante)
        del item._failed_report
        # (La lógica de TRELLO_REPORTING_ENABLED ya está manejada en conftest.py)

    # -----------------------------------------------------------------------------------
    # 2. LÓGICA DE ÉXITO (Cerrar Issue)
    # -----------------------------------------------------------------------------------
    elif report.passed and report.when == "teardown" and not hasattr(item, '_failed_report'):
        logger.info(f"\n[JIRA-HANDLER] Procesando reporte de ÉXITO en Teardown para: {item.name}")

        try:
            jira_client = JiraClient()

            # El ID del caso de prueba es la clave para la búsqueda.
            if not test_case_id or test_case_id == 'N/A':
                logger.debug(f"\n[JIRA-HANDLER] Test sin ID de caso de prueba. No se intentará cerrar Issue.")
                return
            
            # Criterios de búsqueda: (ID del caso) y [Navegador/Dispositivo] y Ambiente
            existing_issue_data = jira_client.find_issue_by_test_id(
                test_case_id, ambiente_actual, navegador_dispositivo_id
            )
            issue_key = existing_issue_data.get('key') if existing_issue_data else None
            
            if issue_key:
                logger.info(f"\n✅ Issue abierto encontrado: {issue_key}. Procediendo a cerrar.")

                # Preparar comentario de éxito (similar a Trello)
                success_comment_body = (
                    f"✅ PRUEBA REPARADA/EXITOSA ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).\n\n"
                    f"### Pasos del Test Ejecutados:\n"
                )
                success_comment_body += "\n".join([f"✅ {paso}" for paso in test_steps_list]) if test_steps_list else "No se registraron pasos de prueba."

                # 2.1. Añadir comentario
                jira_client.add_comment_to_issue(issue_key, success_comment_body)

                # 2.2. Transicionar (Cerrar)
                # La transición a "Cerrado" o "Resuelto" es común.
                jira_client.transition_issue(issue_key, 'Listo')
                logger.info(f"\n✅ Issue {issue_key} transicionado a LISTO.")
            else:
                logger.debug("\n[JIRA-HANDLER] No se encontró Issue abierto asociado al test exitoso. No se requiere acción.")

        except Exception as e:
            logger.critical(f"\n❌ ERROR CRÍTICO: Fallo al procesar el reporte Jira (Éxito) para '{item.nodeid}'. Fallo: {e}", exc_info=True)