import React, { useState, useEffect } from "react";
import { ShieldCheck, ShieldAlert, Loader2, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Select } from "@/components/ui/Select";

export interface CroVerificationResult {
  isValid: boolean;
  status: "ATIVO" | "SUSPENSO" | "CANCELADO" | "INVALIDO" | "PENDENTE";
  verified: boolean;
  canonicalCro?: string;
  professionalName?: string;
  uf?: string;
  cleanNumber?: string;
  category?: string;
  cached?: boolean;
  error?: string;
}

export interface CroVerifiedInputProps {
  value?: string;
  uf?: string;
  category?: "CD" | "EPAO" | "TPD" | "TSB" | "ASB";
  onChange?: (val: { cro: string; uf: string; verified: boolean; canonicalCro: string }) => void;
  disabled?: boolean;
  required?: boolean;
}

const BRAZIL_UFS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
  "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
  "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

const CATEGORY_OPTIONS = [
  { value: "CD", label: "CD (Dentista)" },
  { value: "EPAO", label: "EPAO (Clínica)" },
  { value: "TPD", label: "TPD (Prótese)" },
  { value: "TSB", label: "TSB (Técnico)" },
  { value: "ASB", label: "ASB (Auxiliar)" },
];

const UF_OPTIONS = BRAZIL_UFS.map((u) => ({ value: u, label: u }));

export const CroVerifiedInput: React.FC<CroVerifiedInputProps> = ({
  value = "",
  uf = "SP",
  category = "CD",
  onChange,
  disabled = false,
  required = false,
}) => {
  const [croInput, setCroInput] = useState(value);
  const [selectedUf, setSelectedUf] = useState(uf);
  const [selectedCategory, setSelectedCategory] = useState<"CD" | "EPAO" | "TPD" | "TSB" | "ASB">(category);
  const [loading, setLoading] = useState(false);
  const [verification, setVerification] = useState<CroVerificationResult | null>(null);

  useEffect(() => {
    setCroInput(value);
  }, [value]);

  useEffect(() => {
    setSelectedUf(uf);
  }, [uf]);

  const handleValidate = async () => {
    if (!croInput.trim()) {
      setVerification(null);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/v1/contacts/validate-cro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cro: croInput,
          uf: selectedUf,
          category: selectedCategory,
        }),
      });

      if (!response.ok) {
        throw new Error("Falha na consulta do CRO");
      }

      const data = await response.json();
      const result: CroVerificationResult = {
        isValid: data.is_valid,
        status: data.status,
        verified: data.verified,
        canonicalCro: data.canonical_cro,
        professionalName: data.professional_name,
        uf: data.uf,
        cleanNumber: data.clean_number,
        category: data.category,
        cached: data.cached,
        error: data.error,
      };

      setVerification(result);

      if (onChange) {
        onChange({
          cro: result.canonicalCro || croInput,
          uf: selectedUf,
          verified: result.verified,
          canonicalCro: result.canonicalCro || croInput,
        });
      }
    } catch {
      setVerification({
        isValid: false,
        status: "INVALIDO",
        verified: false,
        error: "Serviço de validação indisponível momentaneamente.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-2 font-sans">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-text-main flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-status-success" />
          Registro Profissional CRO/UF
          {required && <span className="text-status-danger">*</span>}
        </label>

        {verification && (
          <div>
            {verification.verified ? (
              <Badge variant="success" className="gap-1 text-xs">
                <CheckCircle2 className="w-3.5 h-3.5" />
                CRO Verificado Ativo
              </Badge>
            ) : (
              <Badge variant="danger" className="gap-1 text-xs">
                <ShieldAlert className="w-3.5 h-3.5" />
                {verification.status === "SUSPENSO" ? "Registro Suspenso" : "Não Homologado"}
              </Badge>
            )}
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <div className="w-36 shrink-0">
          <Select
            options={CATEGORY_OPTIONS}
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as "CD" | "EPAO" | "TPD" | "TSB" | "ASB")}
            disabled={disabled}
          />
        </div>

        <div className="w-24 shrink-0">
          <Select
            options={UF_OPTIONS}
            value={selectedUf}
            onChange={(e) => setSelectedUf(e.target.value)}
            disabled={disabled}
          />
        </div>

        <div className="relative flex-1">
          <Input
            placeholder="Ex: 123456 ou CRO-SP 123456"
            value={croInput}
            onChange={(e) => setCroInput(e.target.value)}
            onBlur={handleValidate}
            disabled={disabled}
            className="w-full"
          />
        </div>

        <Button
          type="button"
          variant="outline"
          onClick={handleValidate}
          disabled={loading || disabled || !croInput.trim()}
          className="shrink-0"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          <span className="ml-1 hidden sm:inline">Validar</span>
        </Button>
      </div>

      {verification && (
        <div className="text-xs space-y-1">
          {verification.verified && verification.professionalName && (
            <p className="text-status-success font-medium flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Titular: {verification.professionalName} ({verification.canonicalCro})
            </p>
          )}

          {!verification.verified && verification.error && (
            <p className="text-status-danger flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5" />
              {verification.error}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
