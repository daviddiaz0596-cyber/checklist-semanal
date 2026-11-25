import json
import os

import flet as ft

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
CORTO = ["Lun", "Mar", "Mié", "Jue", "Vie"]

# 10 tareas de ejemplo para cada día (puedes cambiarlas desde la app)
TAREAS_BASE = [
    "Revisar correo",
    "Planear el día",
    "Hacer ejercicio",
    "Estudiar 1 hora",
    "Trabajar en el proyecto",
    "Almorzar saludable",
    "Responder mensajes",
    "Ordenar el espacio de trabajo",
    "Leer 20 minutos",
    "Preparar lo de mañana",
]

# En el celular Flet da una carpeta propia para guardar datos; en el computador
# se usa la carpeta del programa.
CARPETA = os.getenv("FLET_APP_STORAGE_DATA") or os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(CARPETA, "tareas.json")


def cargar():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if all(isinstance(datos.get(d), list) for d in DIAS):
            return datos
    except (OSError, ValueError):
        pass
    return {d: [{"texto": t, "hecha": False} for t in TAREAS_BASE] for d in DIAS}


def guardar(datos):
    try:
        os.makedirs(CARPETA, exist_ok=True)
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main(page: ft.Page):
    page.title = "Checklist semanal"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.RED)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.RED)
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    datos = cargar()
    estado = {"dia": 0, "editando": None}

    barra_dias = ft.Row(spacing=6)
    resumen = ft.Text(size=15)
    progreso = ft.ProgressBar(value=0)
    lista = ft.Column(spacing=6)
    nueva = ft.TextField(hint_text="Escribe una tarea nueva", expand=True)

    def tareas():
        return datos[DIAS[estado["dia"]]]

    def cambiar_dia(i):
        estado["dia"] = i
        estado["editando"] = None
        pintar()

    def alternar(i):
        tareas()[i]["hecha"] = not tareas()[i]["hecha"]
        guardar(datos)
        pintar()

    def editar(i):
        estado["editando"] = i
        pintar()

    def guardar_edicion(i, texto):
        texto = texto.strip()
        if texto:
            tareas()[i]["texto"] = texto
        estado["editando"] = None
        guardar(datos)
        pintar()

    def eliminar(i):
        del tareas()[i]
        estado["editando"] = None
        guardar(datos)
        pintar()

    def agregar(e=None):
        texto = nueva.value.strip() if nueva.value else ""
        if texto:
            tareas().append({"texto": texto, "hecha": False})
            nueva.value = ""
            guardar(datos)
            pintar()

    def desmarcar(e=None):
        for t in tareas():
            t["hecha"] = False
        guardar(datos)
        pintar()

    def fila(i, t):
        if estado["editando"] == i:
            campo = ft.TextField(value=t["texto"], expand=True, autofocus=True)
            campo.on_submit = lambda e, i=i, c=campo: guardar_edicion(i, c.value)
            return ft.Row([
                campo,
                ft.Button("Guardar", on_click=lambda e, i=i, c=campo: guardar_edicion(i, c.value)),
            ])

        estilo = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if t["hecha"] else None
        texto = ft.Text(
            t["texto"], size=17, expand=True, style=estilo,
            color=ft.Colors.GREY if t["hecha"] else None,
        )
        icono = ft.Icon(ft.Icons.CHECK_BOX if t["hecha"] else ft.Icons.CHECK_BOX_OUTLINE_BLANK)
        zona_tocable = ft.Container(
            content=ft.Row([icono, texto], expand=True),
            expand=True, padding=10,
            on_click=lambda e, i=i: alternar(i),
        )
        return ft.Row([
            zona_tocable,
            ft.IconButton(ft.Icons.EDIT, on_click=lambda e, i=i: editar(i)),
            ft.IconButton(ft.Icons.CLOSE, on_click=lambda e, i=i: eliminar(i)),
        ])

    def pintar():
        barra_dias.controls = [
            (ft.Button(CORTO[i], expand=True, on_click=lambda e, i=i: cambiar_dia(i))
             if i == estado["dia"] else
             ft.OutlinedButton(CORTO[i], expand=True, on_click=lambda e, i=i: cambiar_dia(i)))
            for i in range(len(DIAS))
        ]
        lt = tareas()
        hechas = sum(1 for t in lt if t["hecha"])
        resumen.value = f"{DIAS[estado['dia']]}: {hechas} de {len(lt)} hechas"
        progreso.value = (hechas / len(lt)) if lt else 0
        lista.controls = [fila(i, t) for i, t in enumerate(lt)]
        page.update()

    nueva.on_submit = agregar

    page.add(
        ft.Row([
            ft.Image(src="icon.png", width=46, height=46, border_radius=12),
            ft.Text("Checklist semanal", size=28, weight=ft.FontWeight.BOLD),
        ]),
        barra_dias,
        ft.Row([resumen, ft.TextButton("Desmarcar todas", on_click=desmarcar)],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        progreso,
        lista,
        ft.Row([nueva, ft.Button("Agregar", on_click=agregar)]),
    )
    pintar()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
