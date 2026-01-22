/**
 * Renders the Double Donut (Ag-Charts Enterprise)
 * Outer: 7 Columns from 'Total général'
 * Inner: SFIL and CAFFIL row sums
 */
function renderAgMultiDonut(tcdData) {
    const { AgCharts } = agCharts;

    const parseFrenchValue = (val) => {
        if (typeof val === 'number') return val;
        if (!val || val === "0,00") return 0;
        // Remove spaces, replace comma with dot
        return Math.abs(parseFloat(val.replace(/\s/g, '').replace(',', '.')) || 0);
    };

    const currencyFormatter = new Intl.NumberFormat("fr-FR", {
        style: "currency", currency: "EUR", maximumFractionDigits: 0
    });

    Object.keys(tcdData).forEach(key => {
        const raw = JSON.parse(tcdData[key]);
        const columns = raw.columns; // ["étiquettes_de_lignes", "Deal_absent_Whp", ...]
        const dataRows = raw.data;

        // 1. PREPARE OUTER RING (The 7 Component Columns from "Total général")
        const totalRow = dataRows.find(row => row[0] === "Total général");
        let outerRingData = [];
        
        if (totalRow) {
            // Start from index 1 to skip the "étiquettes_de_lignes" column
            for (let i = 1; i < columns.length; i++) {
                const val = parseFrenchValue(totalRow[i]);
                if (val > 0) {
                    outerRingData.push({
                        component: columns[i].replace(/_/g, ' '),
                        value: val
                    });
                }
            }
        }

        // 2. PREPARE INNER RING (CAFFIL & SFIL rows)
        let innerRingData = [];
        dataRows.forEach(row => {
            const entityName = row[0];
            if (entityName === "CAFFIL" || entityName === "SFIL") {
                // Sum all numeric columns for this entity
                let totalEntityValue = 0;
                for (let i = 1; i < row.length; i++) {
                    totalEntityValue += parseFrenchValue(row[i]);
                }
                innerRingData.push({
                    entity: entityName,
                    value: totalEntityValue
                });
            }
        });

        const options = {
            container: document.getElementById(`chart-${key}`),
            title: { text: `Analyse ${key.toUpperCase()}`, color: 'white' },
            background: { fill: "transparent" },
            series: [
                {
                    // OUTER RING: Risk Components
                    data: outerRingData,
                    type: "donut",
                    angleKey: "value",
                    sectorLabelKey: "component",
                    outerRadiusRatio: 1,
                    innerRadiusRatio: 0.7,
                    strokeWidth: 2,
                    calloutLabel: { enabled: true, color: "#94a3b8" },
                    tooltip: {
                        renderer: ({ datum }) => ({
                            heading: "Composante",
                            title: datum.component,
                            data: [{ label: "Montant (Abs)", value: currencyFormatter.format(datum.value) }]
                        })
                    }
                },
                {
                    // INNER RING: Entities
                    data: innerRingData,
                    type: "donut",
                    angleKey: "value",
                    sectorLabelKey: "entity",
                    outerRadiusRatio: 0.6,
                    innerRadiusRatio: 0.2,
                    strokeWidth: 2,
                    tooltip: {
                        renderer: ({ datum }) => ({
                            heading: "Entité",
                            title: datum.entity,
                            data: [{ label: "Total Absolu", value: currencyFormatter.format(datum.value) }]
                        })
                    }
                }
            ],
            legend: { enabled: false },
            animation: { enabled: true, duration: 800 }
        };

        AgCharts.create(options);
    });
}

























/**
 * Spreads Chart Logic
 */
function initSpreadUI(spreadRawData) {
    const container = document.getElementById('filterContainer');
    if (!container) return;

    const combos = [...new Set(spreadRawData.map(d => `${d.Prod} | ${d.Dates}`))];
    container.innerHTML = '';
    combos.forEach((c, i) => {
        const l = document.createElement('label');
        l.className = "flex items-center space-x-2 bg-slate-800 px-3 py-2 rounded-xl cursor-pointer border border-slate-700 hover:border-blue-500 transition text-xs";
        l.innerHTML = `<input type="checkbox" class="curve-checkbox" value="${c}" onchange="updateSpreadChart(window.globalSpreadData)" ${i < 2 ? 'checked' : ''}><span>${c}</span>`;
        container.appendChild(l);
    });
    updateSpreadChart(spreadRawData);
}

function updateSpreadChart(spreadRawData) {
    const spreadSelect = document.getElementById('spreadSelect');
    if (!spreadSelect) return;

    const spread = spreadSelect.value;
    const active = Array.from(document.querySelectorAll('.curve-checkbox:checked')).map(cb => cb.value);

    const traces = active.map(combo => {
        const [p, d] = combo.split(' | ');
        const pts = spreadRawData.filter(x => x.Prod === p && x.Dates === d).sort((a, b) => a.MaturiteMonth - b.MaturiteMonth);
        return {
            x: pts.map(x => x.Maturite),
            y: pts.map(x => x[spread]),
            name: combo,
            mode: 'lines+markers',
            line: { shape: 'spline', width: 3 }
        };
    });

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(30, 41, 59, 0.5)',
        font: { color: '#cbd5e1' },
        xaxis: { gridcolor: '#334155', title: 'Maturité' },
        yaxis: { gridcolor: '#334155', title: spread },
        showlegend: true,
        legend: { orientation: "h", yanchor: "bottom", y: -0.3, xanchor: "center", x: 0.5 },
        margin: { t: 40, b: 100, l: 60, r: 40 }
    };
    Plotly.newPlot('mainChart', traces, layout, { responsive: true });
}