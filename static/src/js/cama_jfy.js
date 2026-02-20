/** @odoo-module **/
import { Component, useState, useRef, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { CorteLaser } from "./corte_laser";


export class LaserBed extends Component {
    static components = { CorteLaser };
    setup() {
        this.state = useState({
            materials: Array(9).fill(null),
            reloadFlag: 0,
        });
        this.materialInput = useRef("materialInput");

        this.addMaterial = this.addMaterial.bind(this);
        this.childLoadTrabajos = null;

        onWillStart(async () => {
            await this.getMaterials();
        });
    }

    addMaterial(material, archivo) {
        console.log("Material: ", material);
        // Si hay valor en el input úsalo, si no, recorta el código de la cadena
        const inputValue = this.materialInput?.el?.value;
        const input = inputValue && inputValue.trim() !== ""
            ? inputValue
            : parseInt(material.substring(0, material.indexOf(" -")));

        const nombre = archivo || null;

        console.log("Input: ", input, "Archivo", archivo);

        if (!input) {
            console.error("No se encontró el input materialCode");
            return;
        }

        const code = input;
        if (!code) {
            alert("Por favor ingrese un código de lámina");
            return;
        }

        console.log("this.state.materials: ", this.state.materials);
        const emptyIndex = this.state.materials.findIndex(m => m === null);
        if (emptyIndex === -1) {
            alert("La cama de corte está llena.");
            return;
        }
        const repetido = this.state.materials.find(m => m !== null && m.codigo === code && m.archivo === nombre);
        console.log("Repetido: ", repetido);
        if (repetido) {
            alert("La lámina ya está en la cama de corte.");
            return;
        }

        this.getMaterialCode(code, emptyIndex, nombre);
        if (this.materialInput?.el) {
            this.materialInput.el.value = "";
            this.materialInput.el.focus();
        }
    }

    get occupiedCount() {
        return this.state.materials.filter(m => m !== null).length;
    }

    get availableCount() {
        return this.state.materials.length - this.occupiedCount;
    }

    addContador(index) {
        this.state.materials[index].contador += 1;
        this.addContadorDB(index);
        // this.reloadFlag++;
    }
    async addContadorDB(index) {
        const response = await fetch("/cama_corte_add_contador", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                index: index,
                maquina: "JFY",
                codigo: this.state.materials[index].codigo,
                nombre: `${this.state.materials[index].nombre} ${this.state.materials[index].medida}`,
                cantidad: this.state.materials[index].cantidad,
            }),
        });
        const data = await response.json();
        console.log("Data: ", data);
        console.log("Data: ", data.result["cortado"]);
        if (data.result["cortado"]) {
            this.state.materials[index] = null;
        }
        this.state.reloadFlag++;
    }

    onKeyDown(ev) {
        if (ev.key === "Enter") {
            this.addMaterial();
        }
    }

    removeMaterial(index) {
        if (confirm(`¿Desea quitar la lámina "${this.state.materials[index].codigo}"?`)) {
            this.removeMaterialDB(index);
        }
    }

    startCutting(index) {
        console.log("Materials: ", this.state.materials);
        const permitir = this.state.materials.find(m => m && m.play === true ? true : false);
        console.log("Permitir: ", permitir);
        if (permitir) {
            alert("Ya hay una lámina en corte.");
            return;
        }
        this.state.materials[index].play = true;
        this.startCuttingDB(index);
    }

    async startCuttingDB(index) {
        const response = await fetch("/cama_corte_play", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                index: index,
                maquina: "JFY",
                codigo: this.state.materials[index].codigo,
            }),
        });
        const data = await response.json();
        console.log("Data: ", data);
    }

    stopCutting(index) {
        this.state.materials[index].play = false;
        this.stopCuttingDB(index);
    }

    async stopCuttingDB(index) {
        const response = await fetch("/cama_corte_stop", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                index: index,
                maquina: "JFY",
                codigo: this.state.materials[index].codigo,
            }),
        });
        const data = await response.json();
        console.log("Data: ", data);
    }

    async removeMaterialDB(index) {
        const response = await fetch("/cama_corte_remueve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                index: index,
                maquina: "JFY",
                codigo: this.state.materials[index].codigo,
            }),
        });
        const data = await response.json();
        this.state.materials[index] = null;
    }

    async getMaterials() {
        const response = await fetch("/cama_corte_jfy", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        data.forEach(element => {
            this.state.materials[element.index] = element;
        });
        console.log("Materials: ", this.state.materials);
    }

    async getMaterialCode(codigo, index, archivo) {
        const response = await fetch("/cama_corte_carga", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                codigo: codigo,
                index: index,
                maquina: "JFY",
                archivo: archivo || null,
            }),
        });
        const data = await response.json();
        console.log("Data: ", data);
        if (data.result.error) {
            alert(data.result.error);
            return;
        }
        this.state.materials[index] = data.result;
    }
}
LaserBed.template = "dtm_materiales_laser.maquina_cama_jfy";

registry.category("actions").add('dtm_materiales_laser.maquina_cama_jfy', LaserBed);