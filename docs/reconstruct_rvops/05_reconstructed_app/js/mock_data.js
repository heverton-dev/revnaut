/**
 * Mock Data Engine — Rvops Reconstructed
 * Factual data based on captured sessions, roles and pipelines.
 */

window.RVOPS_DATA = {
  account: {
    id: "0f14ffff",
    name: "Sales Rocket",
    plan: "Enterprise Scale",
    status: "active"
  },
  user: {
    id: "2b08046d-d5e2-4d83-8fd3-b76e184748d7",
    name: "Thiago Hortolan",
    email: "thiago@salesrocketbrasil.com.br",
    role: "Super Admin",
    avatar: "TH"
  },
  metrics: {
    mrr: 142800,
    mrrGrowth: "+14.8%",
    pipelineTotal: 539500,
    dealsCount: 28,
    winRate: "34.2%",
    avgCycleDays: 19
  },
  pipelines: [
    {
      id: 1,
      name: "Funil Enterprise B2B 2026",
      stages: [
        {
          id: 101,
          name: "Qualificação & SDR",
          color: "hsl(208, 67%, 45%)",
          deals: [
            { id: "d-1", title: "Contrato Anual - AgroTech Global", value: 36000, company: "AgroTech Brasil", contact: "Carlos Mendonça", daysInStage: 2, priority: "alta" },
            { id: "d-2", title: "Expansão CRM - Logística Express", value: 18500, company: "LogExpress S/A", contact: "Mariana Alencar", daysInStage: 5, priority: "media" }
          ]
        },
        {
          id: 102,
          name: "Demonstração & Diagnóstico",
          color: "hsl(43, 95%, 45%)",
          deals: [
            { id: "d-3", title: "Implementação RevOps - Fintech Stark", value: 74000, company: "Stark Payments", contact: "Rafael Bittencourt", daysInStage: 4, priority: "alta" },
            { id: "d-4", title: "Migração Hubspot - Rede Varejo Mais", value: 42000, company: "Varejo Mais", contact: "Juliana Frota", daysInStage: 1, priority: "baixa" }
          ]
        },
        {
          id: 103,
          name: "Proposta Comercial",
          color: "hsl(27, 100%, 50%)",
          deals: [
            { id: "d-5", title: "Plataforma Omnichannel - Grupo Alfa", value: 120000, company: "Grupo Alfa Hospitalar", contact: "Dr. Roberto Silveira", daysInStage: 6, priority: "alta" },
            { id: "d-6", title: "Licenciamento 50 Seats - EducarTech", value: 39000, company: "EducarTech Online", contact: "Patrícia Diniz", daysInStage: 8, priority: "media" }
          ]
        },
        {
          id: 104,
          name: "Negociação & Jurídico",
          color: "hsl(280, 60%, 50%)",
          deals: [
            { id: "d-7", title: "Rollout Nacional - Banco Nexus", value: 165000, company: "Nexus Soluções Financeiras", contact: "Fernando Campos", daysInStage: 3, priority: "alta" }
          ]
        },
        {
          id: 105,
          name: "Fechado & Ganho",
          color: "hsl(148, 50%, 45%)",
          deals: [
            { id: "d-8", title: "Onboarding Enterprise - Logística Total", value: 85000, company: "Logística Total", contact: "Carla Pires", daysInStage: 0, priority: "alta" }
          ]
        }
      ]
    }
  ],
  contacts: [
    { id: 1, name: "Carlos Mendonça", email: "carlos@agrotech.com.br", phone: "+55 11 98455-1200", company: "AgroTech Brasil", tags: ["Decisor", "Enterprise", "Inbound"], score: 92, lastActivity: "Hoje às 11:20" },
    { id: 2, name: "Mariana Alencar", email: "mariana.alencar@logexpress.com.br", phone: "+55 19 99123-4567", company: "LogExpress S/A", tags: ["Diretoria", "Follow-up"], score: 78, lastActivity: "Ontem às 16:45" },
    { id: 3, name: "Rafael Bittencourt", email: "rafael@starkpay.io", phone: "+55 11 97788-9900", company: "Stark Payments", tags: ["CTO", "Fintech", "Demo"], score: 96, lastActivity: "Hoje às 09:15" },
    { id: 4, name: "Juliana Frota", email: "jfrota@varejomais.com.br", phone: "+55 21 98877-3322", company: "Varejo Mais", tags: ["Varejo", "Migração"], score: 64, lastActivity: "13/10/2026" },
    { id: 5, name: "Dr. Roberto Silveira", email: "roberto@grupoalfa.med.br", phone: "+55 31 99654-7890", company: "Grupo Alfa Hospitalar", tags: ["VIP", "Proposta"], score: 98, lastActivity: "Hoje às 13:40" },
    { id: 6, name: "Patrícia Diniz", email: "patricia@educartech.com", phone: "+55 41 99234-5678", company: "EducarTech Online", tags: ["EdTech", "Trial Ativo"], score: 70, lastActivity: "12/10/2026" },
    { id: 7, name: "Fernando Campos", email: "fernando.campos@nexusbank.com", phone: "+55 11 98111-2233", company: "Nexus Soluções Financeiras", tags: ["Enterprise", "Jurídico"], score: 95, lastActivity: "Hoje às 14:02" }
  ],
  conversations: [
    {
      id: "chat-1",
      contactName: "Rafael Bittencourt",
      company: "Stark Payments",
      channel: "whatsapp",
      unread: 1,
      lastTime: "14:02",
      messages: [
        { sender: "contact", text: "Olá Thiago, recebemos a apresentação técnica. Muito sólida!", time: "13:58" },
        { sender: "user", text: "Excelente Rafael! Podemos alinhar a homologação dos webhooks na sexta-feira?", time: "14:00" },
        { sender: "contact", text: "Combinado, vou convidar nossa equipe de engenharia para o call.", time: "14:02" }
      ]
    },
    {
      id: "chat-2",
      contactName: "Dr. Roberto Silveira",
      company: "Grupo Alfa Hospitalar",
      channel: "whatsapp",
      unread: 0,
      lastTime: "13:40",
      messages: [
        { sender: "contact", text: "Thiago, o comitê diretivo aprovou a proposta preliminar.", time: "13:30" },
        { sender: "user", text: "Maravilha, Dr. Roberto! Encaminharei a minuta do contrato pelo portal.", time: "13:40" }
      ]
    },
    {
      id: "chat-3",
      contactName: "Mariana Alencar",
      company: "LogExpress S/A",
      channel: "webchat",
      unread: 0,
      lastTime: "Ontem",
      messages: [
        { sender: "contact", text: "Gostaria de saber se o Rvops possui integração nativa com o Blip.", time: "16:40" },
        { sender: "user", text: "Sim Mariana! Conectamos via API REST oficial e Webhooks bidirecionais.", time: "16:45" }
      ]
    }
  ],
  tasks: [
    { id: "t-1", title: "Enviar minuta contratual para Banco Nexus", deal: "Rollout Nacional - Banco Nexus", dueDate: "Hoje", priority: "alta", done: false },
    { id: "t-2", title: "Reunião de alinhamento com engenharia Stark", deal: "Implementação RevOps - Fintech Stark", dueDate: "Amanhã", priority: "alta", done: false },
    { id: "t-3", title: "Follow-up da proposta com Grupo Alfa", deal: "Plataforma Omnichannel - Grupo Alfa", dueDate: "Hoje", priority: "media", done: true },
    { id: "t-4", title: "Verificar limites de disparos de WhatsApp", deal: "Geral da Conta", dueDate: "16/10/2026", priority: "baixa", done: false }
  ]
};
