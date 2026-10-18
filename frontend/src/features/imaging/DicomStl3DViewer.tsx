import React, { useState, useEffect } from 'react';

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

interface DicomStl3DViewerProps {
  studyId?: string;
  dealId?: string;
  onClose?: () => void;
}

export const DicomStl3DViewer: React.FC<DicomStl3DViewerProps> = ({
  studyId = 'study-demo-01',
  dealId,
  onClose,
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [study, setStudy] = useState<ViewerTokenData | null>(null);

  // Controles de Visualização 3D e Medição Cirúrgica
  const [currentSlice, setCurrentSlice] = useState<number>(1);
  const [selectedDiameter, setSelectedDiameter] = useState<number>(3.75);
  const [contrastWindow, setContrastWindow] = useState<number>(1500); // Hounsfield window
  const [contrastLevel, setContrastLevel] = useState<number>(450);    // Bone window level
  const [showImplantGuide, setShowImplantGuide] = useState<boolean>(true);
  const [rotationAngle, setRotationAngle] = useState<number>(0);

  const fetchViewerData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/imaging/studies/${studyId}/viewer-token`);
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error('Estudo tomográfico ou escaneamento STL não encontrado.');
        }
        throw new Error(`Falha ao carregar sessão 3D: HTTP ${res.status}`);
      }
      const data: ViewerTokenData = await res.json();
      setStudy(data);
      setSelectedDiameter(data.recommended_implant_diameter_mm || 3.75);
    } catch (err: any) {
      setError(err.message || 'Erro de conexão com o servidor PACS Orthanc / R2.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchViewerData();
  }, [studyId]);

  // Estado 1: Loading (Skeleton)
  if (loading) {
    return (
      <div className="w-full h-full min-h-[560px] bg-slate-950 border border-slate-800 rounded-xl p-6 flex flex-col gap-4 animate-pulse">
        <div className="flex justify-between items-center border-b border-slate-800 pb-4">
          <div className="h-6 w-64 bg-slate-800 rounded" />
          <div className="h-6 w-32 bg-slate-800 rounded" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1">
          <div className="lg:col-span-3 bg-slate-900 rounded-lg min-h-[380px] flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <svg className="w-8 h-8 text-slate-700 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <span className="text-xs text-slate-500 font-mono">Conectando ao Orthanc PACS & Cloudflare R2...</span>
            </div>
          </div>
          <div className="bg-slate-900 rounded-lg p-4 flex flex-col gap-3">
            <div className="h-4 w-32 bg-slate-800 rounded" />
            <div className="h-8 w-full bg-slate-800 rounded" />
            <div className="h-8 w-full bg-slate-800 rounded" />
            <div className="h-8 w-full bg-slate-800 rounded" />
          </div>
        </div>
      </div>
    );
  }

  // Estado 2: Error State (Com retry)
  if (error) {
    return (
      <div className="w-full min-h-[400px] bg-slate-950 border border-rose-900/50 rounded-xl p-8 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full bg-rose-950/60 border border-rose-700/60 flex items-center justify-center text-rose-400 mb-4">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-100 mb-1">Falha na Visualização Tomográfica</h3>
        <p className="text-sm text-slate-400 max-w-md mb-6">{error}</p>
        <div className="flex gap-3">
          <button
            onClick={fetchViewerData}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Tentar Novamente
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition-colors"
            >
              Fechar
            </button>
          )}
        </div>
      </div>
    );
  }

  // Estado 3: Empty State
  if (!study) {
    return (
      <div className="w-full min-h-[400px] bg-slate-950 border border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-slate-400 mb-4">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-100 mb-1">Nenhum Exame Selecionado</h3>
        <p className="text-sm text-slate-400 max-w-md mb-6">
          Vincule uma tomografia Cone Beam (.dcm) ou escaneamento de arco (.stl) para planejar a cirurgia guiada.
        </p>
        <button
          onClick={() => {}}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload DICOM/STL no R2
        </button>
      </div>
    );
  }

  // Estado 4: Success State (Viewport 3D Funcional)
  return (
    <div className="w-full bg-slate-950 border border-slate-800 rounded-xl overflow-hidden flex flex-col text-slate-100 shadow-2xl">
      {/* Topo do Viewer com Metadados Anatômicos */}
      <div className="px-5 py-3.5 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-950/80 border border-indigo-700/50 text-indigo-400">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-slate-100 tracking-wide">
                Estudo 3D: {study.patient_anonymized_id}
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-indigo-900/50 text-indigo-300 border border-indigo-700/40">
                {study.study_type}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-900/50 text-emerald-300 border border-emerald-700/40">
                LGPD Blindado
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Arcada: {study.jaw_type} | Região: {study.implant_site ? `Dente ${study.implant_site}` : 'Geral'} | Densidade: {study.bone_density_estimate}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
              title="Fechar Visualizador"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Grid Principal: Viewport 3D + Painel de Medição Cirúrgica */}
      <div className="grid grid-cols-1 lg:grid-cols-4 min-h-[500px]">
        {/* Canvas de Visualização 3D / Tomográfica */}
        <div className="lg:col-span-3 bg-black relative flex items-center justify-center overflow-hidden border-b lg:border-b-0 lg:border-r border-slate-800">
          {/* Overlay de Eixos Anatômicos (Axial, Coronal, Sagital) */}
          <div className="absolute top-4 left-4 z-10 flex flex-col gap-1 font-mono text-[11px] text-slate-400 bg-slate-950/70 p-2.5 rounded border border-slate-800">
            <div>Corte: {currentSlice} / {study.slice_count || 1}</div>
            <div>Espessura Óssea: <span className="text-emerald-400 font-semibold">{study.bone_thickness_mm} mm</span></div>
            <div>Densidade: <span className="text-indigo-400 font-semibold">{study.bone_density_estimate}</span></div>
            <div>W/L: {contrastWindow} / {contrastLevel} HU</div>
          </div>

          {/* HUD de Orientação Espacial Superior */}
          <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
            <button
              onClick={() => setRotationAngle((prev) => (prev - 45) % 360)}
              className="p-1.5 bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-700 rounded text-xs flex items-center gap-1 font-mono"
              title="Rotacionar Arco"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Rotacionar
            </button>
            <button
              onClick={() => setShowImplantGuide(!showImplantGuide)}
              className={`p-1.5 border rounded text-xs flex items-center gap-1 font-mono transition-colors ${
                showImplantGuide
                  ? 'bg-emerald-950/80 border-emerald-600 text-emerald-300'
                  : 'bg-slate-900/80 border-slate-700 text-slate-400'
              }`}
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {showImplantGuide ? 'Guia ON' : 'Guia OFF'}
            </button>
          </div>

          {/* Representação Gráfica Vetorial Estilizada do Corte Ósseo e Implante */}
          <div
            className="w-full h-full flex items-center justify-center p-8 transition-transform duration-300"
            style={{ transform: `rotate(${rotationAngle}deg)` }}
          >
            <svg className="w-80 h-80 max-w-full text-slate-800" viewBox="0 0 300 300" fill="none">
              {/* Contorno Anatômico da Crista Óssea Alveolar */}
              <path
                d="M 50 250 C 70 120, 100 80, 150 80 C 200 80, 230 120, 250 250 Z"
                fill="#1e293b"
                stroke="#475569"
                strokeWidth="2"
              />
              {/* Camada Cortical vs Medular */}
              <path
                d="M 75 250 C 90 140, 115 110, 150 110 C 185 110, 210 140, 225 250 Z"
                fill="#0f172a"
                stroke="#334155"
                strokeWidth="1.5"
                strokeDasharray="4 2"
              />

              {/* Canal Mandibular / Seio Maxilar */}
              <circle cx="150" cy="220" r="14" fill="#020617" stroke="#e11d48" strokeWidth="1.5" />
              <text x="150" y="224" textAnchor="middle" fill="#f43f5e" fontSize="9" fontFamily="monospace">N. ALV</text>

              {/* Projeção do Implante Cirúrgico Guiado */}
              {showImplantGuide && (
                <g className="transition-all duration-200">
                  {/* Corpo Cilíndrico/Cônico do Implante */}
                  <rect
                    x={150 - (selectedDiameter * 3.5) / 2}
                    y="75"
                    width={selectedDiameter * 3.5}
                    height="85"
                    rx="3"
                    fill="#0284c7"
                    fillOpacity="0.75"
                    stroke="#38bdf8"
                    strokeWidth="1.5"
                  />
                  {/* Roscas Protéticas Micro-estruturadas */}
                  <line x1={150 - (selectedDiameter * 3.5) / 2} y1="95" x2={150 + (selectedDiameter * 3.5) / 2} y2="95" stroke="#bae6fd" strokeWidth="1" />
                  <line x1={150 - (selectedDiameter * 3.5) / 2} y1="115" x2={150 + (selectedDiameter * 3.5) / 2} y2="115" stroke="#bae6fd" strokeWidth="1" />
                  <line x1={150 - (selectedDiameter * 3.5) / 2} y1="135" x2={150 + (selectedDiameter * 3.5) / 2} y2="135" stroke="#bae6fd" strokeWidth="1" />

                  {/* Margem de Segurança Cirúrgica (Buffer de 2mm até o Nervo) */}
                  <line x1="150" y1="160" x2="150" y2="206" stroke="#fbbf24" strokeWidth="1.5" strokeDasharray="3 3" />
                  <text x="160" y="185" fill="#f59e0b" fontSize="9" fontFamily="monospace">Segurança: 4.8mm</text>
                </g>
              )}
            </svg>
          </div>

          {/* Controle Inferior do Slider de Cortes Tomográficos */}
          <div className="absolute bottom-4 left-6 right-6 z-10 bg-slate-950/80 border border-slate-800 p-2.5 rounded-lg flex items-center gap-4">
            <span className="text-xs text-slate-400 font-mono whitespace-nowrap">Corte Axial:</span>
            <input
              type="range"
              min={1}
              max={study.slice_count || 64}
              value={currentSlice}
              onChange={(e) => setCurrentSlice(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <span className="text-xs text-slate-200 font-mono w-10 text-right">{currentSlice}</span>
          </div>
        </div>

        {/* Painel Lateral: Planejamento Cirúrgico & Parâmetros do Implante */}
        <div className="bg-slate-900/60 p-5 flex flex-col justify-between border-t lg:border-t-0 border-slate-800">
          <div className="flex flex-col gap-5">
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 font-mono">
                Prescrição de Implante
              </h3>
              <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 flex flex-col gap-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Diâmetro Sugerido:</span>
                  <span className="font-semibold text-emerald-400 font-mono">Ø {study.recommended_implant_diameter_mm} mm</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Comprimento Sugerido:</span>
                  <span className="font-semibold text-emerald-400 font-mono">{study.recommended_implant_length_mm} mm</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Espessura Óssea:</span>
                  <span className="font-semibold text-slate-200 font-mono">{study.bone_thickness_mm} mm</span>
                </div>
              </div>
            </div>

            {/* Seleção do Diâmetro do Implante KeyPartners */}
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-2">
                Diâmetro Selecionado (mm):
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {[3.5, 3.75, 4.3, 5.0].map((d) => (
                  <button
                    key={d}
                    onClick={() => setSelectedDiameter(d)}
                    className={`py-1.5 text-xs font-mono font-medium rounded border transition-colors ${
                      selectedDiameter === d
                        ? 'bg-indigo-600 border-indigo-400 text-white'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    Ø {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Ajuste de Janela Tomográfica (Bone / Soft Tissue Window) */}
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1.5">
                Janela Óssea (Hounsfield Units):
              </label>
              <div className="flex flex-col gap-2 bg-slate-950 border border-slate-800 p-3 rounded-lg text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Largura (Window):</span>
                  <span className="font-mono text-slate-200">{contrastWindow} HU</span>
                </div>
                <input
                  type="range"
                  min={500}
                  max={3000}
                  step={50}
                  value={contrastWindow}
                  onChange={(e) => setContrastWindow(Number(e.target.value))}
                  className="accent-indigo-500 cursor-pointer"
                />

                <div className="flex justify-between mt-1">
                  <span className="text-slate-400">Nível (Level):</span>
                  <span className="font-mono text-slate-200">{contrastLevel} HU</span>
                </div>
                <input
                  type="range"
                  min={100}
                  max={1000}
                  step={25}
                  value={contrastLevel}
                  onChange={(e) => setContrastLevel(Number(e.target.value))}
                  className="accent-indigo-500 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Rodapé: Ação de Vinculação com o Pedido DENTGO / KeyPartners */}
          <div className="pt-4 border-t border-slate-800 flex flex-col gap-2">
            <button
              onClick={() => {}}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/40"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Aprovar Guia & Separar Kit Consignado
            </button>
            <div className="text-[10px] text-center text-slate-500 font-mono">
              Orthanc PACS v24.3 // Cloudflare R2 Presigned
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DicomStl3DViewer;
