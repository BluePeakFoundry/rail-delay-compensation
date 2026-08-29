function rateForDelay(minutes) {
  if (minutes >= 120) return 0.50;
  if (minutes >= 60) return 0.25;
  return 0;
}

function euro(amount) {
  return `${amount.toFixed(2)} €`;
}

function draftText(ticket, delay, rate, amount) {
  const pct = Math.round(rate * 100);
  if (rate === 0) {
    return 'Borrador no generado: el retraso indicado no alcanza el umbral orientativo de 60 minutos. Revisa el procedimiento oficial del operador si hubo otras incidencias.';
  }
  return [
    'Asunto: Solicitud de revisión por retraso ferroviario',
    '',
    'Hola,',
    `Solicito la revisión de mi viaje ferroviario por un retraso de llegada de ${delay} minutos.`,
    `Según la estimación orientativa preparada, el reembolso mínimo podría ser del ${pct}% sobre un billete de ${euro(ticket)}, equivalente a ${euro(amount)}.`,
    'Adjunto o conservaré la documentación del viaje y quedo pendiente del procedimiento oficial aplicable.',
    '',
    'Esta solicitud debe adaptarse con datos reales y verificarse con las condiciones del operador antes de enviarse.'
  ].join('\n');
}

function setResult(message, draft) {
  document.getElementById('result').innerHTML = message;
  document.getElementById('draft').value = draft;
}

function calculate() {
  const ticket = Number(document.getElementById('ticket').value || 0);
  const delay = Number(document.getElementById('delay').value || 0);
  const covered = document.getElementById('covered').checked;
  const exceptional = document.getElementById('exceptional').checked;
  if (!Number.isFinite(ticket) || ticket < 0 || !Number.isFinite(delay) || delay < 0) {
    setResult('<p>Introduce valores válidos y no negativos.</p>', '');
    return;
  }
  if (!covered) {
    setResult('<p>Fuera de alcance orientativo: verifica las normas del país, operador y tipo de servicio.</p>', '');
    return;
  }
  if (exceptional) {
    setResult('<p>Posible exclusión o condición especial. Revisa las condiciones oficiales del operador antes de preparar una reclamación.</p>', '');
    return;
  }
  const rate = rateForDelay(delay);
  const amount = Math.round(ticket * rate * 100) / 100;
  const pct = Math.round(rate * 100);
  const message = `<p><strong>Retraso:</strong> ${delay} min · <strong>Tasa mínima orientativa:</strong> ${pct}% · <strong>Estimación:</strong> ${euro(amount)}.</p><p>La cifra no garantiza aceptación ni pago. Comprueba siempre el procedimiento del operador.</p>`;
  setResult(message, draftText(ticket, delay, rate, amount));
  if (window.BluePeakAnalytics) window.BluePeakAnalytics.track('conversion:rail:calculation-complete', 'Rail calculation complete');
}

document.getElementById('calculate').addEventListener('click', calculate);
for (const id of ['ticket', 'delay', 'covered', 'exceptional']) {
  document.getElementById(id).addEventListener('input', calculate);
  document.getElementById(id).addEventListener('change', calculate);
}
calculate();


function downloadRailDraft() {
  const text = document.getElementById('draft').value || '';
  const blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'rail-delay-compensation-draft.txt';
  link.click();
  URL.revokeObjectURL(url);
  if (window.BluePeakAnalytics) window.BluePeakAnalytics.track('conversion:rail:download-draft', 'Rail draft downloaded');
}

document.getElementById('download-draft').addEventListener('click', downloadRailDraft);
