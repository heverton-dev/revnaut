/**
 * RevNault LiveKit WebRTC & VoIP Room Module
 * Gerenciamento de conexao WebRTC, discagem SIP e gravacao R2.
 */

export const LiveKitRoomModule = {
  activeRoom: null,

  async fetchToken(roomName, identity, dealId = null) {
    const response = await fetch('/api/v1/communications/rooms/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        room_name: roomName,
        identity: identity,
        deal_id: dealId,
      }),
    });
    if (!response.ok) {
      throw new Error(`Erro ao gerar token da sala: ${response.statusText}`);
    }
    return await response.json();
  },

  async dialVoip(phoneNumber, roomName, dealId = null) {
    const response = await fetch('/api/v1/communications/voip/dial', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone_number: phoneNumber,
        room_name: roomName,
        deal_id: dealId,
      }),
    });
    if (!response.ok) {
      throw new Error(`Erro ao discar VoIP SIP: ${response.statusText}`);
    }
    return await response.json();
  },

  async getDealRecordings(dealId) {
    const response = await fetch(`/api/v1/communications/deals/${dealId}/recordings`);
    if (!response.ok) {
      throw new Error(`Erro ao listar gravacoes: ${response.statusText}`);
    }
    return await response.json();
  },
};
