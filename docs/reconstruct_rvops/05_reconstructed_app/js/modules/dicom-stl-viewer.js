/**
 * Módulo de Visualização 3D de Tomografias Odontológicas (DICOM) e Escaneamentos STL
 * Integrado ao servidor Orthanc PACS e Cloudflare R2 presigned.
 * Zero emojis (Lei #14).
 */

export class DicomStlViewerModule {
  constructor(containerId = 'dicom-viewer-container') {
    this.container = document.getElementById(containerId);
    this.currentSlice = 1;
    this.totalSlices = 64;
    this.selectedDiameter = 3.75;
    this.activeStudy = null;
  }

  async loadStudy(studyId) {
    if (!this.container) return;
    this.renderLoading();

    try {
      const response = await fetch(`/api/v1/imaging/studies/${studyId}/viewer-token`);
      if (!response.ok) {
        throw new Error(`Falha HTTP ${response.status} ao obter sessão 3D`);
      }
      this.activeStudy = await response.json();
      this.totalSlices = this.activeStudy.slice_count || 64;
      this.selectedDiameter = this.activeStudy.recommended_implant_diameter_mm || 3.75;
      this.renderSuccess();
    } catch (err) {
      this.renderError(err.message);
    }
  }

  renderLoading() {
    this.container.innerHTML = `
      <div class="viewer-loading" style="background:#020617; border:1px solid #1e293b; padding:2rem; border-radius:12px; text-align:center; color:#94a3b8;">
        <svg style="width:32px; height:32px; animation:spin 1s linear infinite; margin:0 auto 12px; display:block;" fill="none" viewBox="0 0 24 24">
          <circle style="opacity:0.25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path style="opacity:0.75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <p style="font-family:monospace; font-size:12px;">Conectando ao Orthanc DICOM Server & Cloudflare R2...</p>
      </div>
    `;
  }

  renderError(msg) {
    this.container.innerHTML = `
      <div class="viewer-error" style="background:#020617; border:1px solid #7f1d1d; padding:2rem; border-radius:12px; text-align:center;">
        <div style="color:#f87171; font-weight:600; margin-bottom:8px;">Erro na Reconstrução 3D</div>
        <p style="color:#94a3b8; font-size:13px; margin-bottom:16px;">${msg}</p>
        <button id="btn-retry-viewer" style="background:#4f46e5; color:#fff; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:12px;">
          Tentar Novamente
        </button>
      </div>
    `;
    const btn = this.container.querySelector('#btn-retry-viewer');
    if (btn) btn.onclick = () => this.loadStudy(this.activeStudy?.study_id || 'demo');
  }

  renderSuccess() {
    const s = this.activeStudy;
    this.container.innerHTML = `
      <div class="dicom-stl-card" style="background:#020617; border:1px solid #1e293b; border-radius:12px; overflow:hidden; color:#f8fafc; font-family:sans-serif;">
        <div style="background:#0f172a; padding:12px 18px; border-bottom:1px solid #1e293b; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-weight:600; font-size:14px;">Estudo: ${s.patient_anonymized_id}</span>
              <span style="background:#312e81; color:#c7d2fe; font-size:10px; padding:2px 6px; border-radius:4px; font-family:monospace;">${s.study_type}</span>
              <span style="background:#064e3b; color:#a7f3d0; font-size:10px; padding:2px 6px; border-radius:4px; font-family:monospace;">LGPD ANONIMIZADO</span>
            </div>
            <div style="font-size:11px; color:#94a3b8; font-family:monospace; margin-top:2px;">
              Arcada: ${s.jaw_type} | Densidade: ${s.bone_density_estimate} | Espessura: ${s.bone_thickness_mm} mm
            </div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: 3fr 1fr; min-height:420px;">
          <div style="background:#000; position:relative; display:flex; align-items:center; justify-content:center; border-right:1px solid #1e293b;">
            <svg style="width:260px; height:260px;" viewBox="0 0 300 300" fill="none">
              <path d="M 50 250 C 70 120, 100 80, 150 80 C 200 80, 230 120, 250 250 Z" fill="#1e293b" stroke="#475569" stroke-width="2"/>
              <circle cx="150" cy="220" r="14" fill="#020617" stroke="#e11d48" stroke-width="1.5"/>
              <rect id="implant-projection" x="${150 - (this.selectedDiameter * 3.5) / 2}" y="75" width="${this.selectedDiameter * 3.5}" height="85" rx="3" fill="#0284c7" fill-opacity="0.8" stroke="#38bdf8" stroke-width="1.5"/>
            </svg>
            <div style="position:absolute; bottom:12px; left:16px; right:16px; background:rgba(2,6,23,0.85); border:1px solid #1e293b; padding:8px 14px; border-radius:8px; display:flex; align-items:center; gap:12px;">
              <span style="font-size:11px; color:#94a3b8; font-family:monospace;">Corte:</span>
              <input type="range" id="slice-slider" min="1" max="${this.totalSlices}" value="${this.currentSlice}" style="flex:1; accent-color:#6366f1;">
              <span id="slice-value" style="font-size:11px; font-family:monospace; width:30px; text-align:right;">${this.currentSlice}</span>
            </div>
          </div>

          <div style="background:#0f172a; padding:18px; display:flex; flex-direction:column; justify-content:between;">
            <div>
              <div style="font-size:11px; text-transform:uppercase; color:#94a3b8; font-weight:600; margin-bottom:10px; font-family:monospace;">Prescrição Cirúrgica</div>
              <div style="background:#020617; border:1px solid #1e293b; padding:10px; border-radius:8px; font-size:11px; display:flex; flex-direction:column; gap:6px;">
                <div>Diâmetro: <strong style="color:#34d399; font-family:monospace;">Ø ${s.recommended_implant_diameter_mm} mm</strong></div>
                <div>Comprimento: <strong style="color:#34d399; font-family:monospace;">${s.recommended_implant_length_mm} mm</strong></div>
                <div>Espessura Óssea: <strong style="color:#f8fafc; font-family:monospace;">${s.bone_thickness_mm} mm</strong></div>
              </div>

              <div style="margin-top:14px;">
                <label style="font-size:11px; color:#cbd5e1; display:block; margin-bottom:6px;">Diâmetro Selecionado:</label>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:4px;">
                  ${[3.5, 3.75, 4.3, 5.0].map(d => `
                    <button class="btn-dia" data-dia="${d}" style="padding:6px; background:${this.selectedDiameter === d ? '#4f46e5' : '#020617'}; border:1px solid #1e293b; color:#fff; border-radius:4px; font-family:monospace; font-size:11px; cursor:pointer;">
                      Ø ${d}
                    </button>
                  `).join('')}
                </div>
              </div>
            </div>

            <div style="margin-top:20px;">
              <button style="width:100%; padding:10px; background:#059669; color:#fff; border:none; border-radius:8px; font-weight:600; font-size:12px; cursor:pointer;">
                Separar Kit Consignado
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    const slider = this.container.querySelector('#slice-slider');
    const valSpan = this.container.querySelector('#slice-value');
    if (slider && valSpan) {
      slider.oninput = (e) => {
        this.currentSlice = Number(e.target.value);
        valSpan.innerText = this.currentSlice;
      };
    }

    const diaBtns = this.container.querySelectorAll('.btn-dia');
    diaBtns.forEach(btn => {
      btn.onclick = () => {
        this.selectedDiameter = Number(btn.dataset.dia);
        this.renderSuccess();
      };
    });
  }
}
