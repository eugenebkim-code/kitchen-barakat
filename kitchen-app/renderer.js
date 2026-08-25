const config = window.KITCHEN_CONFIG || {};
const WS_URL = config.WS_URL;
const WS_TOKEN = config.WS_TOKEN;
const API_BASE_URL = config.API_BASE_URL || '';

// Exponential backoff per spec: 1s, 2s, 5s, 10s (capped)
const RECONNECT_DELAYS = [1000, 2000, 5000, 10000];
let reconnectAttempt = 0;
let ws = null;

const orderQueue = [];
let currentOrder = null;

const el = {
  connectionDot: document.getElementById('connection-dot'),
  connectionText: document.getElementById('connection-text'),
  clock: document.getElementById('clock'),
  idleScreen: document.getElementById('idle-screen'),
  orderScreen: document.getElementById('order-screen'),
  orderId: document.getElementById('order-id'),
  orderTypeBadge: document.getElementById('order-type-badge'),
  orderPhone: document.getElementById('order-phone'),
  addressRow: document.getElementById('address-row'),
  orderAddress: document.getElementById('order-address'),
  commentRow: document.getElementById('comment-row'),
  orderComment: document.getElementById('order-comment'),
  orderItems: document.getElementById('order-items'),
  orderTotal: document.getElementById('order-total'),
  receiptImg: document.getElementById('receipt-img'),
  queueBadge: document.getElementById('queue-badge'),
  ackButton: document.getElementById('ack-button'),
  siren: document.getElementById('siren'),
};

function updateClock() {
  const now = new Date();
  const formatted = now.toLocaleString('ru-RU', {
    timeZone: 'Asia/Seoul',
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  el.clock.textContent = `${formatted} KST`;
}
setInterval(updateClock, 1000);
updateClock();

function setConnectionStatus(status) {
  el.connectionDot.className = 'dot ' + status;
  if (status === 'connected') {
    el.connectionText.textContent = 'Подключено';
  } else if (status === 'connecting') {
    el.connectionText.textContent = 'Подключение...';
  } else {
    const idx = Math.min(reconnectAttempt, RECONNECT_DELAYS.length - 1);
    const seconds = RECONNECT_DELAYS[idx] / 1000;
    el.connectionText.textContent = `Нет связи, переподключение через ${seconds}с...`;
  }
}

function connect() {
  if (!WS_URL || !WS_TOKEN) {
    el.connectionDot.className = 'dot reconnecting';
    el.connectionText.textContent = 'Ошибка: заполните config.js (см. config.example.js)';
    return;
  }

  setConnectionStatus(reconnectAttempt > 0 ? 'reconnecting' : 'connecting');

  const url = `${WS_URL}?token=${encodeURIComponent(WS_TOKEN)}`;
  ws = new WebSocket(url);

  ws.onopen = () => {
    reconnectAttempt = 0;
    setConnectionStatus('connected');
  };

  ws.onmessage = (event) => {
    let frame;
    try {
      frame = JSON.parse(event.data);
    } catch (err) {
      console.error('Bad WS frame (not JSON):', event.data, err);
      return;
    }
    if (frame.event === 'NEW_ORDER' && frame.order) {
      enqueueOrder(frame.order);
    }
  };

  ws.onclose = () => {
    scheduleReconnect();
  };

  ws.onerror = () => {
    ws.close();
  };
}

function scheduleReconnect() {
  setConnectionStatus('reconnecting');
  const delay = RECONNECT_DELAYS[Math.min(reconnectAttempt, RECONNECT_DELAYS.length - 1)];
  reconnectAttempt++;
  setTimeout(connect, delay);
}

function enqueueOrder(order) {
  orderQueue.push(order);
  if (!currentOrder) {
    showNextOrder();
  } else {
    updateQueueBadge();
  }
  playSiren();
}

function showNextOrder() {
  currentOrder = orderQueue.shift() || null;
  updateQueueBadge();

  if (!currentOrder) {
    el.idleScreen.classList.remove('hidden');
    el.orderScreen.classList.add('hidden');
    stopSiren();
    return;
  }

  el.idleScreen.classList.add('hidden');
  el.orderScreen.classList.remove('hidden');
  renderOrder(currentOrder);
}

function renderOrder(order) {
  el.orderId.textContent = order.id;

  const isDelivery = order.order_type === 'delivery';
  el.orderTypeBadge.textContent = isDelivery ? '🛵 ДОСТАВКА' : '🛍️ САМОВЫВОЗ';
  el.orderTypeBadge.className = 'badge ' + (isDelivery ? 'delivery' : 'pickup');

  el.orderPhone.textContent = order.phone || '';

  if (order.address) {
    el.addressRow.classList.remove('hidden');
    el.orderAddress.textContent = order.address;
  } else {
    el.addressRow.classList.add('hidden');
  }

  if (order.comment) {
    el.commentRow.classList.remove('hidden');
    el.orderComment.textContent = order.comment;
  } else {
    el.commentRow.classList.add('hidden');
  }

  el.orderItems.innerHTML = '';
  (order.items || []).forEach((item) => {
    const row = document.createElement('div');
    row.className = 'item-row';

    const nameSpan = document.createElement('span');
    nameSpan.textContent = `${item.name} × ${item.qty}`;

    const priceSpan = document.createElement('span');
    priceSpan.textContent = `${(item.price * item.qty).toLocaleString('ko-KR')} ₩`;

    row.appendChild(nameSpan);
    row.appendChild(priceSpan);
    el.orderItems.appendChild(row);
  });

  el.orderTotal.textContent = `${(order.total_amount || 0).toLocaleString('ko-KR')} ₩`;

  if (order.screenshot_url) {
    const src = /^https?:\/\//i.test(order.screenshot_url)
      ? order.screenshot_url
      : `${API_BASE_URL}${order.screenshot_url}`;
    el.receiptImg.src = src;
    el.receiptImg.classList.remove('hidden');
  } else {
    el.receiptImg.removeAttribute('src');
    el.receiptImg.classList.add('hidden');
  }
}

function updateQueueBadge() {
  if (orderQueue.length > 0) {
    el.queueBadge.textContent = `Ещё в очереди: ${orderQueue.length}`;
    el.queueBadge.classList.remove('hidden');
  } else {
    el.queueBadge.classList.add('hidden');
  }
}

function playSiren() {
  el.siren.currentTime = 0;
  el.siren.play().catch((err) => console.error('Audio play failed:', err));
}

function stopSiren() {
  el.siren.pause();
  el.siren.currentTime = 0;
}

el.ackButton.addEventListener('click', () => {
  stopSiren();
  showNextOrder();
  if (currentOrder) {
    playSiren();
  }
});

connect();
