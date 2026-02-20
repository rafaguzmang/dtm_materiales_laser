/** @odoo-module */

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";


export class CorteLaser extends Component {
    static props = ["material", "reloadFlag?"];
    setup() {
        this.state = useState({
            trabajos: [],
            showPDF: false,
            currentPDF: null,
            pdfTitle: ''
        });

        onWillStart(async () => {
            await this.loadTrabajos();
        });

        onWillUpdateProps((nextProps) => {
            if (nextProps.reloadFlag !== this.props.reloadFlag) {
                this.loadTrabajos();
            }
        });
    }

    playAgregar(lamina, archivo) {
        console.log("Lamina: ", lamina);
        this.props.material(lamina, archivo);
    }

    async loadTrabajos() {
        const response = await fetch('/dtm_corte_laser');
        const data = await response.json();
        let index = 0;
        const trabajos = data.map(row => ({ id: index++, ...row }));
        this.state.trabajos = trabajos;
        console.log("Trabajos: ", this.state.trabajos);
    }

    openPDF(trabajo) {
        console.log("Trabajo: ", trabajo);
        this.state.currentPDF = trabajo.documentos; // El base64 del PDF
        this.state.pdfTitle = trabajo.nombre;
        this.state.showPDF = true;
    }


    closePDF() {
        this.state.showPDF = false;
        this.state.currentPDF = null;
        this.state.pdfTitle = '';
    }
}

CorteLaser.template = "dtm_materiales_laser.corte_laser_view";