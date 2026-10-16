# Manual da Rota: Ensino & Kits Acadêmicos (`/#institutions`)

## 1. Objetivo da Rota
Gerenciar o relacionamento comercial com faculdades de odontologia, centros de pós-graduação (como São Leopoldo Mandic, ABO, APCD) e professores formadores de opinião. Foco no fornecimento de kits acadêmicos, patrocínio de cursos cirúrgicos e captação antecipada de futuros especialistas.

---

## 2. O Que o Usuário Consegue Realizar
* Cadastrar e visualizar universidades e institutos de pós-graduação em implantodontia.
* Gerenciar turmas de especialização e cronogramas de módulos clínicos presenciais.
* Controlar a entrega e o comodato de kits acadêmicos para estudantes de pós-graduação.
* Monitorar a conversão de alunos em cirurgiões prescritores da marca após a formatura.

---

## 3. Quem Pode Ver e Realizar Ações (Matriz RBAC)

| Perfil | Visualizar Instituições | Criar Parcerias | Aprovar Kits Acadêmicos com Desconto |
|---|---|---|---|
| Consultor Especialista em Ensino | Sim (instituições sob sua gestão) | Sim | Não (requer aprovação da gerência) |
| Gerente de Contas Estratégicas | Sim (regional) | Sim | Sim (até limite de alçada da BU) |
| Diretor Comercial | Sim (nacional) | Sim | Sim |
| Super Admin | Sim (acesso total) | Sim | Sim |

---

## 4. Quais Ações Podem Ser Realizadas
* `REGISTER_INSTITUTION`: Cadastrar polo universitário, coordenador do curso e quantidade de alunos por turma.
* `DISPATCH_ACADEMIC_KIT`: Emitir pedido de fornecimento de kit acadêmico com condições diferenciadas.
* `SPONSOR_HANDS_ON`: Alocar materiais e motores cirúrgicos para aulas práticas de laboratório (Hands-On).

---

## 5. Como o Usuário Realiza as Ações (Passo a Passo)
1. Acesse **Comercial & CRM > Ensino & Kits Acadêmicos**.
2. Localize a instituição desejada (ex: "Faculdade São Leopoldo Mandic - Campinas").
3. Clique em "Ver Turmas & Módulos".
4. Verifique a listagem de alunos da especialização de implantodontia.
5. Para registrar entrega de kits, clique em "Registrar Kit Acadêmico", selecione os alunos contemplados e defina a forma de pagamento facilitada.

---

## 6. O Que Falta Implementar (Roadmap & Gaps)
* Portal do Aluno com acesso a vídeos técnicos e manuais de cirurgia guiada.
* Emissão automatizada de certificado de treinamento prático na linha de implantes.
* Rastreamento da migração do aluno formando para sua primeira clínica privada.
