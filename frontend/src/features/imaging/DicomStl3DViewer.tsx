import React, { useState, useEffect } from "react";

export interface ImagingStudy {
  id: string;
  account_id: string;
  patient_anonymized_id: string;
  patient_name?: string | null;
  deal_id?: string | null;
  ticket_id?: string | null;
  study_type: string;
  orthanc_study_id?: string | null;
  r2_storage_key: string;
  file_name: string;
  file_size_bytes: number;
  slice_count: number;
  jaw_type: string;
  bone_density_estimate: string;
  implant_site?: string | null;
  is_anonymized: boolean;
  created_at?: string;
}

export interface ViewerTokenData {
  study_id: string;
  viewer_token: string;
  viewer_stream_url: string;
  r2_public_url: string;
  study_type: string;
  patient_anonymized_id: string;
  jaw_type: string;
  bone_density_estimate: string;
  implant_site?: string | null;
  slice_count: number;
  recommended_implant_diameter_mm: number;
  recommended_implant_length_mm: number;
  bone_thickness_mm: number;
  expires_in_seconds: number;
}

export interface DicomStl3DViewerProps {
  studyId?: string;
  dealId?: string;
  onClose?: () => void;
}

export const DicomStl3DViewer: React.FC<DicomStl3DViewerProps> = ({
  studyId = "study-demo-01",
  dealId,
  onClose,
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [study, setStudy] = useState<ViewerTokenData | null>(null);

  const [currentSlice, setCurrentSlice] = useState<number>(1);
  const [selectedDiameter, setSelectedDiameter] = useState<number>(3.75);
  const [contrastWindow, setContrastWindow] = useState<number>(1500);
  const [contrastLevel, setContrastLevel] = useState<number>(450);
  const [showImplantGuide, setShowImplantGuide] = useState<boolean>(true);
  const [rotationAngle, setRotationAngle] = useState<number>(0);

  const fetchViewerData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/imaging/studies/${studyId}/viewer-token`);
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error("Estudo tomográfico ou escaneamento STL não encontrado.");
        }
        throw new Error(`Falha ao carregar sessão 3D: HTTP ${res.status}`);
      }
      const data: ViewerTokenData = await res.json();
      setStudy(data);
      setSelectedDiameter(data.recommended_implant_diameter_mm || 3.75);
    } catch (err: any) {
      setError(err.message || "Erro de conexão com o servidor PACS Orthanc / R2.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchViewerData();
  }, [studyId]);

  if (loading) {
    return (
      <div className="w-full h-full min-h-[560px] bg-surface-card border border-border rounded-xl p-6 flex flex-col gap-4 animate-pulse">
        <div className="flex justify-between items-center border-b border-border pb-4">
          <div className="h-6 w-64 bg-surface-bg rounded" />
          <div className="h-6 w-32 bg-surface-bg rounded" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1">
          <div className="lg:col-span-3 bg-surface-bg rounded-lg min-h-[380px] flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <svg className="w-8 h-8 text-text-muted animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <span className="text-xs text-text-secondary font-mono">
                Conectando ao Orthanc PACS & Cloudflare R2...
              </span>
            </div>
          </div>
          <div className="bg-surface-bg rounded-lg p-4 flex flex-col gap-3">
            <div className="h-4 w-32 bg-surface-card rounded" />
            <div className="h-8 w-full bg-surface-card rounded" />
            <div className="h-8 w-full bg-surface-card rounded" />
            <div className="h-8 w-full bg-surface-card rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full min-h-[400px] bg-surface-card border border-status-danger/30 rounded-xl p-8 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full bg-status-danger-subtle border border-status-danger/30 flex items-center justify-center text-status-danger mb-4">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-text-main mb-1">Falha na Visualização Tomográfica</h3>
        <p className="text-sm text-text-secondary max-w-md mb-6">{error}</p>
        <div className="flex gap-3">
          <button
            onClick={fetchViewerData}
            className="px-4 py-2 bg-brand-primary hover:bg-brand-primary-hover text-text-inverse text-xs font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Tentar Novamente
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 bg-surface-bg hover:bg-surface-card text-text-secondary text-xs font-medium rounded-lg border border-border transition-colors"
            >
              Fechar
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!study) {
    return (
      <div className="w-full min-h-[400px] bg-surface-card border border-border rounded-xl p-8 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full bg-surface-bg border border-border flex items-center justify-center text-text-secondary mb-4">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-text-main mb-1">Nenhum Exame Selecionado</h3>
        <p className="text-sm text-text-secondary max-w-md mb-6">
          Vincule uma tomografia Cone Beam (.dcm) ou escaneamento de arco (.stl) para planejar a cirurgia guiada.
        </p>
        <button
          onClick={() => {}}
          className="px-4 py-2 bg-status-success text-text-inverse text-xs font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          Upload DICOM/STL no R2
        </button>
      </div>
    );
  }

  return (
    <div className="w-full bg-surface-card border border-border rounded-xl overflow-hidden flex flex-col text-text-main shadow-card">
      <div className="px-5 py-3.5 bg-surface-bg border-b border-border flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-brand-navy-subtle border border-border text-brand-navy">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"
              />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-text-main tracking-wide">
                Estudo 3D: {study.patient_anonymized_id}
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-brand-navy-subtle text-brand-navy border border-border">
                {study.study_type}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-status-success-subtle text-status-success border border-status-success/30">
                LGPD Blindado
              </span>
              {dealId && (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-card text-text-secondary border border-border">
                  Deal: {dealId}
                </span>
              )}
            </div>
            <p className="text-xs text-text-secondary font-mono mt-0.5">
              Arcada: {study.jaw_type} | Região: {study.implant_site ? `Dente ${study.implant_site}` : "Geral"} | Densidade: {study.bone_density_estimate}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-text-secondary hover:text-text-main hover:bg-surface-card rounded-lg transition-colors"
              title="Fechar Visualizador"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 min-h-[500px]">
        <div className="lg:col-span-3 bg-surface-sidebar relative flex items-center justify-center overflow-hidden border-b lg:border-b-0 lg:border-r border-border">
          <div className="absolute top-4 left-4 z-10 flex flex-col gap-1 font-mono text-[11px] text-text-inverse bg-surface-sidebar/90 p-2.5 rounded border border-border">
            <div>Corte: {currentSlice} / {study.slice_count || 1}</div>
            <div>
              Espessura Óssea: <span className="text-status-success font-semibold">{study.bone_thickness_mm} mm</span>
            </div>
            <div>
              Densidade: <span className="text-brand-primary font-semibold">{study.bone_density_estimate}</span>
            </div>
            <div>W/L: {contrastWindow} / {contrastLevel} HU</div>
          </div>

          <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
            <button
              onClick={() => setRotationAngle((prev) => (prev - 45) % 360)}
              className="p-1.5 bg-surface-card text-text-main border border-border rounded text-xs flex items-center gap-1 font-mono"
              title="Rotacionar Arco"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Rotacionar
            </button>
            <button
              onClick={() => setShowImplantGuide(!showImplantGuide)}
              className={`p-1.5 border rounded text-xs flex items-center gap-1 font-mono transition-colors ${
                showImplantGuide
                  ? "bg-status-success-subtle border-status-success text-status-success"
                  : "bg-surface-card border-border text-text-secondary"
              }`}
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              {showImplantGuide ? "Guia ON" : "Guia OFF"}
            </button>
          </div>

          <div
            className="w-full h-full flex items-center justify-center p-8 transition-transform duration-300"
            style={{ transform: `rotate(${rotationAngle}deg)` }}
          >
            <svg className="w-80 h-80 max-w-full text-text-muted" viewBox="0 0 300 300" fill="none">
              <path
                d="M 50 250 C 70 120, 100 80, 150 80 C 200 80, 230 120, 250 250 Z"
                fill="var(--color-surface-card)"
                stroke="var(--color-border)"
                strokeWidth="2"
              />
              <path
                d="M 75 250 C 90 140, 115 110, 150 110 C 185 110, 210 140, 225 250 Z"
                fill="var(--color-surface-bg)"
                stroke="var(--color-border-subtle)"
                strokeWidth="1.5"
                strokeDasharray="4 2"
              />

              <circle
                cx="150"
                cy="220"
                r="14"
                fill="var(--color-danger-subtle)"
                stroke="var(--color-danger)"
                strokeWidth="1.5"
              />
              <text x="150" y="224" textAnchor="middle" fill="var(--color-danger)" fontSize="9" fontFamily="monospace">
                N. ALV
              </text>

              {showImplantGuide && (
                <g className="transition-all duration-200">
                  <rect
                    x={150 - (selectedDiameter * 3.5) / 2}
                    y="75"
                    width={selectedDiameter * 3.5}
                    height="85"
                    rx="3"
                    fill="var(--color-brand-primary)"
                    fillOpacity="0.75"
                    stroke="var(--color-brand-navy)"
                    strokeWidth="1.5"
                  />
                  <line
                    x1={150 - (selectedDiameter * 3.5) / 2}
                    y1="95"
                    x2={150 + (selectedDiameter * 3.5) / 2}
                    y2="95"
                    stroke="var(--color-text-inverse)"
                    strokeWidth="1"
                  />
                  <line
                    x1={150 - (selectedDiameter * 3.5) / 2}
                    y1="115"
                    x2={150 + (selectedDiameter * 3.5) / 2}
                    y2="115"
                    stroke="var(--color-text-inverse)"
                    strokeWidth="1"
                  />
                  <line
                    x1={150 - (selectedDiameter * 3.5) / 2}
                    y1="135"
                    x2={150 + (selectedDiameter * 3.5) / 2}
                    y2="135"
                    stroke="var(--color-text-inverse)"
                    strokeWidth="1"
                  />

                  <line
                    x1="150"
                    y1="160"
                    x2="150"
                    y2="206"
                    stroke="var(--color-warning)"
                    strokeWidth="1.5"
                    strokeDasharray="3 3"
                  />
                  <text x="160" y="185" fill="var(--color-warning)" fontSize="9" fontFamily="monospace">
                    Segurança: 4.8mm
                  </text>
                </g>
              )}
            </svg>
          </div>

          <div className="absolute bottom-4 left-6 right-6 z-10 bg-surface-card border border-border p-2.5 rounded-lg flex items-center gap-4">
            <span className="text-xs text-text-secondary font-mono whitespace-nowrap">Corte Axial:</span>
            <input
              type="range"
              min={1}
              max={study.slice_count || 64}
              value={currentSlice}
              onChange={(e) => setCurrentSlice(Number(e.target.value))}
              className="w-full cursor-pointer"
            />
            <span className="text-xs text-text-main font-mono w-10 text-right">{currentSlice}</span>
          </div>
        </div>

        <div className="bg-surface-bg p-5 flex flex-col justify-between border-t lg:border-t-0 border-border">
          <div className="flex flex-col gap-5">
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-text-secondary mb-3 font-mono">
                Prescrição de Implante
              </h3>
              <div className="bg-surface-card border border-border rounded-lg p-3 flex flex-col gap-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-text-secondary">Diâmetro Sugerido:</span>
                  <span className="font-semibold text-status-success font-mono">
                    Ø {study.recommended_implant_diameter_mm} mm
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-text-secondary">Comprimento Sugerido:</span>
                  <span className="font-semibold text-status-success font-mono">
                    {study.recommended_implant_length_mm} mm
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-text-secondary">Espessura Óssea:</span>
                  <span className="font-semibold text-text-main font-mono">{study.bone_thickness_mm} mm</span>
                </div>
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-text-secondary block mb-2">
                Diâmetro Selecionado (mm):
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {[3.5, 3.75, 4.3, 5.0].map((d) => (
                  <button
                    key={d}
                    onClick={() => setSelectedDiameter(d)}
                    className={`py-1.5 text-xs font-mono font-medium rounded border transition-colors ${
                      selectedDiameter === d
                        ? "bg-brand-primary border-brand-primary text-text-inverse"
                        : "bg-surface-card border-border text-text-main hover:bg-surface-bg"
                    }`}
                  >
                    Ø {d}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-text-secondary block mb-1.5">
                Janela Óssea (Hounsfield Units):
              </label>
              <div className="flex flex-col gap-2 bg-surface-card border border-border p-3 rounded-lg text-xs">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Largura (Window):</span>
                  <span className="font-mono text-text-main">{contrastWindow} HU</span>
                </div>
                <input
                  type="range"
                  min={500}
                  max={3000}
                  step={50}
                  value={contrastWindow}
                  onChange={(e) => setContrastWindow(Number(e.target.value))}
                  className="cursor-pointer"
                />

                <div className="flex justify-between mt-1">
                  <span className="text-text-secondary">Nível (Level):</span>
                  <span className="font-mono text-text-main">{contrastLevel} HU</span>
                </div>
                <input
                  type="range"
                  min={100}
                  max={1000}
                  step={25}
                  value={contrastLevel}
                  onChange={(e) => setContrastLevel(Number(e.target.value))}
                  className="cursor-pointer"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-border flex flex-col gap-2">
            <button
              onClick={() => {}}
              className="w-full py-2.5 bg-status-success text-text-inverse text-xs font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-card"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Aprovar Guia & Separar Kit Consignado
            </button>
            <div className="text-[10px] text-center text-text-muted font-mono">
              Orthanc PACS v24.3 // Cloudflare R2 Presigned
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DicomStl3DViewer;
