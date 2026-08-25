function rateForDelay(minutes) {
  if (minutes >= 120) return 0.50;
  if (minutes >= 60) return 0.25;
  return 0;
}

function calculate() {
  const ticket = Number(document.getElementById('ticket').value || 0);
  const delay = Number(document.getElementById('delay').value || 0);
  const covered = document.getElementById('covered').checked;
  const exceptional = document.getElementById('exceptional').checked;
  const result = document.getElementById('result');
  if (!covered) {
    result.textContent = 'Fuera de alcance orientativo: verifica las normas del país y del operador.';
    return;
  }
  if (exceptional) {
    result.textContent = 'Posible exclusión por circunstancias excepcionales. Revisa las condiciones del operador.';
    return;
  }
  const rate = rateForDelay(delay);
  const amount = Math.round(ticket * rate * 100) / 100;
  result.innerHTML = `<h2>Resultado orientativo</h2><p>Retraso: ${delay} min · Tasa mínima orientativa: ${Math.round(rate * 100)}% · Estimación: ${amount.toFixed(2)} €.</p><p>La cifra no garantiza que la reclamación sea aceptada. Comprueba siempre las condiciones del operador.</p>`;
}

document.getElementById('calculate').addEventListener('click', calculate);
calculate();
