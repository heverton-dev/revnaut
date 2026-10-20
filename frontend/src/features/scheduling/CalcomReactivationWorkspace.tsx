import * as React from "react";
import {
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Send,
  CalendarCheck,
  Plus,
  Video,
  ChevronLeft,
  ChevronRight,
  Lock,
} from "lucide-react";
import { LiveKitDealRoomModal } from "@/features/communications/LiveKitDealRoomModal";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { DataTable, Column } from "@/components/ui/DataTable";

interface ReactivationScheduleItem {
  id: string;
  patient_name: string;
  patient_phone: string;
  surgeon_name: string;
  procedure_name: string;
  surgery_date: string;
  milestone_days: number;
  scheduled_dispatch_date: string;
  calcom_booking_link: string;
  status: string;
}

interface CalcomBookingItem {
  id: string;
  calcom_booking_uid: string;
  patient_name: string;
  patient_phone?: string;
  host_name?: string;
  event_type_title: string;
  start_time: string;
  meeting_url?: string;
  deal_id?: string;
  task_id?: string;
  status: string;
}

export const CalcomReactivationWorkspace: React.FC = () => {
  const [schedules, setSchedules] = React.useState<ReactivationScheduleItem[]>([]);
  const [bookings, setBookings] = React.useState<CalcomBookingItem[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [feedbackMsg, setFeedbackMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  // Formulário Programar Ciclo 6/12/18m
  const [patientName, setPatientName] = React.useState<string>("Roberto Silveira");
  const [patientPhone, setPatientPhone] = React.useState<string>("+5511991234567");
  const [surgeonName, setSurgeonName] = React.useState<string>("Dr. Lucas Mendes");
  const [procedureName, setProcedureName] = React.useState<string>("Protocolo All-on-4 Superior");
  const [surgeryDate, setSurgeryDate] = React.useState<string>("2026-01-15");
  const [scheduling, setScheduling] = React.useState<boolean>(false);
  const [scanning, setScanning] = React.useState<boolean>(false);
  const [weekOffset, setWeekOffset] = React.useState<number>(0);
  const [videoBooking, setVideoBooking] = React.useState<CalcomBookingItem | null>(null);

  const loadCalcomData = React.useCallback(async () => {
    setLoading(true);
    try {
      const [schedRes, bookRes] = await Promise.all([
        fetch("/api/v1/automations/calcom/schedules"),
        fetch("/api/v1/automations/calcom/bookings"),
      ]);
      if (schedRes.ok) {
        const sData = await schedRes.json();
        setSchedules(Array.isArray(sData) ? sData : []);
      }
      if (bookRes.ok) {
        const bData = await bookRes.json();
        setBookings(Array.isArray(bData) ? bData : []);
      }
    } catch {
      // Silencioso
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadCalcomData();
  }, [loadCalcomData]);

  const handleScheduleReactivation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientName.trim()) return;
    setScheduling(true);
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const res = await fetch("/api/v1/automations/calcom/schedule-reactivation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_name: patientName.trim(),
          patient_phone: patientPhone.trim(),
          surgeon_name: surgeonName.trim(),
          procedure_name: procedureName.trim(),
          surgery_date: surgeryDate,
          calcom_event_slug: "manutencao-peri-implantar",
          base_calcom_url: "https://cal.com/dr-lucas-mendes",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao programar ciclos preventivos.");
      setFeedbackMsg(
        `3 janelas profiláticas (180d, 365d e 540d) agendadas para ${data.patient_name}!`
      );
      await loadCalcomData();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setScheduling(false);
    }
  };

  const handleScanDispatches = async () => {
    setScanning(true);
    setErrorMsg(null);
    setFeedbackMsg(null);
    try {
      const res = await fetch("/api/v1/automations/calcom/scan-dispatches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reference_date: "2026-10-18",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao executar varredura de disparos.");
      setFeedbackMsg(
        `Varredura concluída: ${data.scanned_count} ciclos verificados, ${data.dispatched_count} convites WhatsApp disparados.`
      );
      await loadCalcomData();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setScanning(false);
    }
  };

  const slotHours = Array.from({ length: 11 }, (_, i) => 8 + i); // 08:00 .. 18:00

  const weekDays = React.useMemo(() => {
    const base = new Date();
    base.setHours(0, 0, 0, 0);
    const dow = base.getDay(); // 0=dom
    const mondayShift = dow === 0 ? 1 : 1 - dow;
    base.setDate(base.getDate() + mondayShift + weekOffset * 7);
    return Array.from({ length: 5 }, (_, i) => {
      const d = new Date(base);
      d.setDate(base.getDate() + i);
      return d;
    });
  }, [weekOffset]);

  const bookedSlotKeys = React.useMemo(() => {
    const keys = new Set<string>();
    for (const b of bookings) {
      const t = new Date(b.start_time);
      if (!Number.isNaN(t.getTime())) keys.add(`${t.getFullYear()}-${t.getMonth()}-${t.getDate()}-${t.getHours()}`);
    }
    return keys;
  }, [bookings]);

  const handlePickSlot = (day: Date, hour: number) => {
    const start = new Date(day);
    start.setHours(hour, 0, 0, 0);
    void handleSimulateBookingWebhook(undefined, start);
  };

  const handleSimulateBookingWebhook = async (sched?: ReactivationScheduleItem, slotStart?: Date) => {
    setErrorMsg(null);
    setFeedbackMsg(null);
    const targetPatient = sched?.patient_name || patientName || "Paciente Retorno";
    const targetPhone = sched?.patient_phone || patientPhone || "+5511991234567";
    const targetSurgeon = sched?.surgeon_name || surgeonName || "Dr. Lucas Mendes";
    try {
      const res = await fetch("/api/v1/automations/calcom/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          triggerEvent: "BOOKING_CREATED",
          payload: {
            uid: `cal_uid_${Date.now()}`,
            title: "Manutenção Peri-implantar & Profilaxia Protocolo",
            startTime: (slotStart || new Date("2026-11-10T14:00:00.000Z")).toISOString(),
            endTime: new Date(
              (slotStart || new Date("2026-11-10T14:00:00.000Z")).getTime() + 45 * 60 * 1000,
            ).toISOString(),
            location: "integrations:livekit",
            organizer: {
              name: targetSurgeon,
              email: "cirurgiao@revnaut.internal",
            },
            attendees: [
              {
                name: targetPatient,
                email: "paciente@clinica.internal",
              },
            ],
            metadata: {
              patient_phone: targetPhone,
            },
          },
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Falha ao processar webhook Cal.com.");
      setFeedbackMsg(
        `Booking #${data.booking_uid} confirmado! Deal de Kit Peri-implantar #${data.deal_id} e Tarefa #${data.task_id} gerados automaticamente.`
      );
      await loadCalcomData();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const scheduleColumns: Column<ReactivationScheduleItem>[] = [
    {
      key: "patient_name",
      header: "Paciente & Procedimento",
      render: (s) => (
        <div>
          <div className="font-semibold text-text-main">{s.patient_name}</div>
          <div className="text-xs text-text-secondary">
            {s.procedure_name} • {s.surgeon_name}
          </div>
        </div>
      ),
    },
    {
      key: "milestone_days",
      header: "Janela Profilática",
      render: (s) => (
        <Badge variant="navy" className="text-[10px]">
          {s.milestone_days} dias ({Math.round(s.milestone_days / 30)} meses)
        </Badge>
      ),
    },
    {
      key: "scheduled_dispatch_date",
      header: "Data de Disparo",
      render: (s) => <span className="text-xs font-mono text-text-main">{s.scheduled_dispatch_date}</span>,
    },
    {
      key: "status",
      header: "Status & Confirmação",
      render: (s) => (
        <div className="flex items-center gap-2">
          <Badge
            variant={
              s.status === "BOOKED"
                ? "success"
                : s.status === "DISPATCHED"
                ? "default"
                : "secondary"
            }
            className="text-[10px]"
          >
            {s.status}
          </Badge>
          {s.status !== "BOOKED" && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleSimulateBookingWebhook(s);
              }}
              className="text-xs font-medium text-brand-primary hover:underline"
            >
              Confirmar Retorno
            </button>
          )}
        </div>
      ),
    },
  ];

  const bookingColumns: Column<CalcomBookingItem>[] = [
    {
      key: "patient_name",
      header: "Paciente Confirmado",
      render: (b) => (
        <div>
          <div className="font-semibold text-text-main">{b.patient_name}</div>
          <div className="text-xs text-text-secondary">{b.event_type_title}</div>
        </div>
      ),
    },
    {
      key: "start_time",
      header: "Horário Agendado",
      render: (b) => <span className="text-xs font-mono text-text-main">{b.start_time}</span>,
    },
    {
      key: "deal_id",
      header: "Kit Peri-Implantar / Deal",
      render: (b) => (
        <Badge variant="success" className="text-[10px]">
          Deal #{b.deal_id || "Gerado"}
        </Badge>
      ),
    },
    {
      key: "meeting_url",
      header: "Teleconsulta",
      render: (b) => (
        <Button size="sm" variant="secondary" onClick={() => setVideoBooking(b)} className="gap-1.5">
          <Video className="h-3.5 w-3.5 text-brand-primary" />
          Abrir Teleconsulta LiveKit
        </Button>
      ),
    },
  ];

  const dispatchedCount = schedules.filter((s) => s.status === "DISPATCHED").length;
  const bookedCount = schedules.filter((s) => s.status === "BOOKED").length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-main">
            Motor Cal.com • Reativação Preventiva de Pacientes (6 / 12 / 18 Meses)
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            Automação de retorno profilático pós-implante com disparo de convite WhatsApp e criação automática de oportunidade de kit de manutenção peri-implantar.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleScanDispatches}
            disabled={scanning}
            className="gap-1.5"
          >
            <Send className="h-3.5 w-3.5" />
            {scanning ? "Varrendo..." : "Executar Varredura de Disparos Pendentes"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const pending = schedules.find((s) => s.status !== "BOOKED");
              if (pending) {
                handleSimulateBookingWebhook(pending);
              } else {
                setFeedbackMsg("Nenhum agendamento pendente para confirmação 1-clique.");
              }
            }}
            className="gap-1.5"
          >
            <CalendarCheck className="h-3.5 w-3.5" />
            Confirmacao 1-Clique
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              try {
                const res = await fetch("/api/v1/automations/calcom/webhook", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    triggerEvent: "SCHEDULE_BLOCKED_MATERIAL",
                    payload: { status: "BLOQUEADO_MATERIAL" },
                  }),
                });
                const data = await res.json().catch(() => ({}));
                if (!res.ok) throw new Error(data.detail || "Falha ao bloquear agenda por falta de material.");
                setFeedbackMsg(`Bloqueio de agenda ativado: ${data.affected_slots ?? 0} slots marcados como BLOQUEADO_MATERIAL.`);
                await loadCalcomData();
              } catch (err: any) {
                setErrorMsg(err.message || "Erro ao bloquear agenda.");
              }
            }}
            className="gap-1.5"
          >
            <Lock className="h-3.5 w-3.5" />
            Bloquear Agenda (Falta Material)
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleSimulateBookingWebhook()}
            className="gap-1.5"
          >
            <CalendarCheck className="h-3.5 w-3.5" />
            Simular Booking Webhook
          </Button>
          <Button variant="ghost" size="sm" onClick={loadCalcomData} className="gap-1.5">
            <RefreshCw className="h-3.5 w-3.5" />
            Atualizar
          </Button>
        </div>
      </div>

      {feedbackMsg && (
        <div className="p-3 rounded-lg bg-status-success-subtle border border-status-success/30 text-xs text-status-success flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{feedbackMsg}</span>
          </div>
          <button type="button" onClick={() => setFeedbackMsg(null)} className="underline">
            Fechar
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-3 rounded-lg bg-status-danger-subtle border border-status-danger/30 text-xs text-status-danger flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button type="button" onClick={() => setErrorMsg(null)} className="underline">
            Fechar
          </button>
        </div>
      )}

      {/* KPIs de Retorno Profilático */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-border">
          <span className="text-xs font-semibold uppercase text-text-secondary">
            Ciclos Programados (6/12/18m)
          </span>
          <p className="text-xl font-bold text-text-main mt-1">{schedules.length}</p>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs font-semibold uppercase text-text-secondary">
            Convites WhatsApp Disparados
          </span>
          <p className="text-xl font-bold text-brand-primary mt-1">{dispatchedCount}</p>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs font-semibold uppercase text-text-secondary">
            Consultas Confirmadas (Bookings)
          </span>
          <p className="text-xl font-bold text-status-success mt-1">
            {bookings.length || bookedCount}
          </p>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs font-semibold uppercase text-text-secondary">
            Kits Peri-Implantares Gerados
          </span>
          <p className="text-xl font-bold text-brand-navy mt-1">{bookings.length}</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-brand-primary" />
              Programar Ciclo de Reativação (6/12/18m)
            </CardTitle>
            <CardDescription>
              Calcula deterministicamente os retornos de 180, 365 e 540 dias a partir da cirurgia.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleScheduleReactivation} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  Nome do Paciente Reabilitado *
                </label>
                <Input
                  required
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  WhatsApp do Paciente *
                </label>
                <Input
                  required
                  value={patientPhone}
                  onChange={(e) => setPatientPhone(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  Cirurgião Responsável *
                </label>
                <Input
                  required
                  value={surgeonName}
                  onChange={(e) => setSurgeonName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  Procedimento Realizado *
                </label>
                <Input
                  required
                  value={procedureName}
                  onChange={(e) => setProcedureName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">
                  Data da Cirurgia de Instalação *
                </label>
                <Input
                  type="date"
                  required
                  value={surgeryDate}
                  onChange={(e) => setSurgeryDate(e.target.value)}
                />
              </div>
              <Button type="submit" size="sm" disabled={scheduling} className="w-full gap-1.5">
                <Plus className="h-3.5 w-3.5" />
                {scheduling ? "Agendando..." : "Programar Janelas 6/12/18 Meses"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="lg:col-span-2 space-y-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-brand-primary" />
                Agenda de Disparos Preventivos (180d / 365d / 540d)
              </CardTitle>
              <CardDescription>
                Listagem de pacientes monitorados e links de agendamento Cal.com gerados.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                columns={scheduleColumns}
                data={schedules}
                isLoading={loading}
                defaultPageSize={25}
                emptyTitle="Nenhum ciclo preventivo programado"
                emptyDescription="Utilize o formulário ao lado para agendar os retornos de 6, 12 e 18 meses."
              />
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-brand-primary" />
                Agenda Visual de Retornos (Seg a Sex, 08:00 a 18:00)
              </CardTitle>
              <CardDescription>
                Clique em um horário livre para confirmar o retorno do paciente via Cal.com.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Button size="sm" variant="outline" onClick={() => setWeekOffset((w) => w - 1)} aria-label="Semana anterior">
                  <ChevronLeft className="h-3.5 w-3.5" />
                </Button>
                <span className="text-xs font-semibold text-text-main">
                  {weekDays[0].toLocaleDateString("pt-BR")} a {weekDays[4].toLocaleDateString("pt-BR")}
                </span>
                <Button size="sm" variant="outline" onClick={() => setWeekOffset((w) => w + 1)} aria-label="Próxima semana">
                  <ChevronRight className="h-3.5 w-3.5" />
                </Button>
              </div>
              <div className="overflow-x-auto">
                <div className="grid gap-1 min-w-[560px]" style={{ gridTemplateColumns: "56px repeat(5, minmax(0, 1fr))" }}>
                  <div />
                  {weekDays.map((d) => (
                    <div key={d.toISOString()} className="text-center text-[11px] font-semibold text-text-secondary pb-1">
                      {d.toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "2-digit" })}
                    </div>
                  ))}
                  {slotHours.map((h) => (
                    <React.Fragment key={h}>
                      <div className="text-[11px] font-mono text-text-muted self-center">{String(h).padStart(2, "0")}:00</div>
                      {weekDays.map((d) => {
                        const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}-${h}`;
                        const taken = bookedSlotKeys.has(key);
                        const past = new Date(d.getFullYear(), d.getMonth(), d.getDate(), h).getTime() < Date.now();
                        return (
                          <button
                            key={key}
                            type="button"
                            disabled={taken || past}
                            onClick={() => handlePickSlot(d, h)}
                            aria-label={`${d.toLocaleDateString("pt-BR")} ${h}:00 ${taken ? "ocupado" : "disponível"}`}
                            className={`py-1.5 rounded border text-[10px] transition ${
                              taken
                                ? "bg-status-success-subtle text-status-success border-status-success/30"
                                : past
                                ? "bg-surface-bg text-text-muted border-border opacity-50 cursor-not-allowed"
                                : "bg-surface-card text-text-main border-border hover:border-brand-primary hover:bg-brand-primary-subtle"
                            }`}
                          >
                            {taken ? "Confirmado" : past ? "-" : "Livre"}
                          </button>
                        );
                      })}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CalendarCheck className="h-4 w-4 text-status-success" />
                Consultas de Manutenção Confirmadas via Cal.com
              </CardTitle>
              <CardDescription>
                Cada agendamento confirmado gera automaticamente um Deal de Kit Peri-Implantar no funil comercial.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                columns={bookingColumns}
                data={bookings}
                isLoading={loading}
                defaultPageSize={25}
                emptyTitle="Nenhuma consulta confirmada ainda"
                emptyDescription="Clique em 'Simular Booking Webhook' ou 'Confirmar Retorno' para registrar uma confirmação Cal.com."
              />
            </CardContent>
          </Card>
        </div>
      </div>

      {videoBooking && (
        <LiveKitDealRoomModal
          isOpen
          onClose={() => setVideoBooking(null)}
          dealId={String(videoBooking.deal_id || videoBooking.id)}
          dealTitle={videoBooking.event_type_title}
          contactName={videoBooking.patient_name}
          contactPhone={videoBooking.patient_phone}
        />
      )}
    </div>
  );
};

export default CalcomReactivationWorkspace;
