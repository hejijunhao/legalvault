# backend/admin/views.py
from fastapi_admin.resources import Field, Model

@app.register
class VirtualParalegalAdmin(Model):
    label = "Virtual Paralegals"
    model = VirtualParalegal
    icon = "fas fa-robot"  # FontAwesome icon
    page_pre_title = "virtual paralegals list"
    page_title = "Virtual Paralegals Management"
    fields = [
        "id",
        Field(name="name", label="Name"),
    ]