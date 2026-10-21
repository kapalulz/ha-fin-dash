/* Findash cards v0.4.0 — all six cards in one file: Overview, Money flow, Today, Limits,
   Forecast, Game. No build step, no external dependencies. Data comes from the Findash
   integration sensors; no token is ever needed here. All text goes through textContent.
   Every block of every card can be switched off: `show_<block>: false` (visual editor:
   checkboxes). Lists (`tiles`, `limits`) choose what to show and in which order. */
const FD_VERSION = '0.4.0';
const FD_TEXT = {
  ru: {
    overview: 'Мои деньги', flow: 'Куда идут деньги', today: 'Сегодня', limits: 'Лимиты на месяц',
    forecast: 'Прогноз', game: 'Летопись героя',
    debit: 'Дебит', credit: 'Кредит', cushion: 'Подушка', free: 'Свободно',
    debitHint: 'Остатки на включённых текущих и сберегательных счетах', creditHint: 'Долг по кредитным картам',
    cushionHint: 'Включённые инвестиционные и пенсионные счета', freeHint: 'Дебит − кредит − обязательные платежи до конца месяца',
    plan: 'План', now: 'Этот месяц', income: 'Доход', mandatory: 'Обязательные платежи', left: 'После платежей',
    need: 'Необходимое', pocket: 'Карманные', prepay: 'Досрочка ипотеки', buffer: 'Запас', one_off: 'Разовые покупки',
    rest: 'Не распределено', available: 'Осталось сейчас', short: 'Не хватает', end: 'На конец месяца',
    ahead: 'Ещё ожидается', bills: 'Ещё платежей', ifNothing: 'Если больше не тратить', updated: 'Рассчитано',
    emptyFlow: 'Пока нет данных для распределения',
    canSpend: 'Можно потратить сегодня', daysLeft: n => `осталось ${n} дн. в месяце`,
    spentOf: (a, b) => `${a} из ${b}`, piggy: 'В копилке', monthMark: 'Сколько месяца прошло',
    over: 'Хватит в этом месяце', noLimit: 'лимит не задан', carry: 'перенос', noLimits: 'Лимиты появятся, когда накопится история трат',
    allGood: 'Все лимиты в норме',
    min: 'Минимум на счетах', low: 'Уйдёт в минус — перенесите траты или переведите деньги заранее',
    nextIncome: 'Зарплата', nextPayment: 'Ближайший платёж', nowShort: 'Сейчас', after: n => `Через ${n} дн.`,
    level: 'Уровень', xp: 'опыта', streak: 'Серия', days: 'дн.', best: 'рекорд', quests: 'Задания на сегодня',
    achievements: 'Достижения', hp: 'HP', hits: n => `ударов: ${n}`, maxLevel: 'Максимальный уровень',
    missing: 'Датчик не найден', multiple: 'Несколько датчиков — выберите Entity в настройках',
    noSensor: 'Нет датчика Findash — обновите интеграцию и сервер Findash', unavailable: 'Findash недоступен',
    invalid: 'Некорректное значение', tileUnavailable: 'Недоступно',
    flowMissing: 'Сущность не найдена', flowNoSensor: 'Home Assistant ещё не передал датчик с данными Findash',
    flowMultiple: 'Найдено несколько датчиков Findash — укажите entity', flowInvalid: 'У датчика нет данных flow для карточки',
  },
  en: {
    overview: 'My money', flow: 'Where the money goes', today: 'Today', limits: 'Monthly limits',
    forecast: 'Forecast', game: "Hero's chronicle",
    debit: 'Debit', credit: 'Credit', cushion: 'Cushion', free: 'Free',
    debitHint: 'Balances of enabled checking and savings accounts', creditHint: 'Credit card debt',
    cushionHint: 'Enabled investment and retirement accounts', freeHint: 'Debit − credit − bills still due this month',
    plan: 'Plan', now: 'This month', income: 'Income', mandatory: 'Bills', left: 'After bills',
    need: 'Needs', pocket: 'Pocket money', prepay: 'Mortgage prepayment', buffer: 'Buffer', one_off: 'One-off purchases',
    rest: 'Unallocated', available: 'Left now', short: 'Shortfall', end: 'At month end',
    ahead: 'Income still expected', bills: 'Bills still due', ifNothing: 'If nothing more is spent', updated: 'Calculated',
    emptyFlow: 'No allocation data yet',
    canSpend: 'You can spend today', daysLeft: n => `${n} days left this month`,
    spentOf: (a, b) => `${a} of ${b}`, piggy: 'Piggy bank', monthMark: 'Month elapsed',
    over: 'Enough for this month', noLimit: 'no limit set', carry: 'carry', noLimits: 'Limits appear once there is spending history',
    allGood: 'All limits are fine',
    min: 'Lowest balance', low: 'Goes below zero — move spending or transfer money in advance',
    nextIncome: 'Payday', nextPayment: 'Next payment', nowShort: 'Now', after: n => `In ${n} days`,
    level: 'Level', xp: 'XP', streak: 'Streak', days: 'd', best: 'best', quests: "Today's quests",
    achievements: 'Achievements', hp: 'HP', hits: n => `hits: ${n}`, maxLevel: 'Max level',
    missing: 'Sensor not found', multiple: 'Multiple sensors — select an Entity in settings',
    noSensor: 'No Findash sensor — update the integration and the Findash server', unavailable: 'Findash unavailable',
    invalid: 'Invalid value', tileUnavailable: 'Unavailable',
    flowMissing: 'Entity not found', flowNoSensor: 'Home Assistant has not provided a sensor with Findash data yet',
    flowMultiple: 'Multiple Findash sensors found — specify entity', flowInvalid: 'This sensor has no flow data for the card',
  },
};
const FD_STATE = { ok: 'var(--success-color, #43a047)', warn: 'var(--warning-color, #ffa000)',
  full: 'var(--error-color, #db4437)', none: 'var(--disabled-text-color, #9e9e9e)' };
const FD_RARITY = { common: '#9e9e9e', uncommon: '#1eaa00', rare: '#2f80d6', epic: '#9b4fe0', legendary: '#ff8000' };
const FD_FLOW_COLORS = { need: '#5187ba', pocket: '#ba9641', prepay: '#489b83', buffer: '#997eb5',
  one_off: 'repeating-linear-gradient(135deg, var(--secondary-text-color) 0 2px, transparent 2px 5px)' };
const FD_TILES = ['debit', 'credit', 'cushion', 'free'];
const FD_CSS = `
  :host{display:block;height:100%;container-type:inline-size}
  ha-card{display:block;box-sizing:border-box;height:100%;overflow:auto;padding:20px;color:var(--primary-text-color);font-family:var(--paper-font-body1_-_font-family,sans-serif)}
  h2{font-size:20px;font-weight:600;margin:0 0 16px;letter-spacing:-.3px}
  .muted{color:var(--secondary-text-color);font-size:12px}.empty{padding:16px 0;color:var(--secondary-text-color)}
  .row{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin:8px 0;font-size:14px}
  .label{display:flex;align-items:center;gap:9px}
  b{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}.negative{color:var(--error-color,#db4437)}
  .track{position:relative;height:10px;border-radius:5px;background:var(--secondary-background-color,#eee);margin:6px 0 2px}
  .fill{height:100%;border-radius:5px;max-width:100%}
  .mark{position:absolute;top:-3px;width:2px;height:16px;border-radius:1px;background:var(--primary-text-color)}
  button.tap{all:unset;display:block;box-sizing:border-box;width:100%;cursor:pointer;border-radius:8px}
  button.tap:focus-visible,button:focus-visible{outline:2px solid var(--primary-color);outline-offset:3px}
  @container(max-width:330px){ha-card{padding:14px}h2{font-size:18px}}`;

/* ---------------------------------------------------------------------------------------- */
/** Common part: config, sensor lookup, error states, helpers, `show_*` switches. */
class FindashCard extends HTMLElement {
  static metric = '';      // findash_metric of the sensor this card reads
  static blocks = [];      // [key, ru, en]: the parts that can be switched off
  static ownTitle = false; // the card draws its title itself (next to its tabs)
  constructor() { super(); this.attachShadow({ mode: 'open' }); }
  setConfig(config) {
    if (config.entity != null && typeof config.entity !== 'string') throw new Error('entity must be an Entity ID string');
    if (config.language && !['ru', 'en'].includes(config.language)) throw new Error('language: ru | en');
    this.check(config);
    this._config = { ...config, entity: typeof config.entity === 'string' ? config.entity.trim() : '' };
    this.render();
  }
  check() {}
  set hass(hass) {
    const previous = this._hass; this._hass = hass;
    if (!previous || previous.states !== hass.states || previous.language !== hass.language) this.render();
  }
  static getConfigElement() { const el = document.createElement('findash-card-editor'); el.card = this; return el; }
  static getStubConfig() { return {}; }
  getCardSize() { return 4; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: 4, min_rows: 2 }; }
  show(key) { return this._config[`show_${key}`] !== false; }
  resolve(matcher = s => s.attributes.findash_metric === this.constructor.metric) {
    const states = this._hass.states;
    if (this._config.entity) return { id: this._config.entity, state: states[this._config.entity] };
    const ids = Object.keys(states).filter(id => id.startsWith('sensor.') && matcher(states[id]));
    return ids.length === 1 ? { id: ids[0], state: states[ids[0]] } : { multiple: ids.length > 1 };
  }
  el(tag, text, cls, parent) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    if (parent) parent.append(node);
    return node;
  }
  bar(parent, pct, color, mark) {
    const track = this.el('div', null, 'track', parent);
    const fill = this.el('div', null, 'fill', track);
    fill.style.width = `${Math.max(Math.min(pct, 1), 0) * 100}%`; fill.style.background = color;
    if (mark != null) { const m = this.el('div', null, 'mark', track); m.style.left = `calc(${Math.min(mark, 1) * 100}% - 1px)`; m.title = this.t.monthMark; }
    return track;
  }
  tap(parent, id, cls = '') {
    const b = this.el('button', null, `tap ${cls}`, parent); b.type = 'button';
    b.addEventListener('click', () => this.dispatchEvent(new CustomEvent('hass-more-info', { detail: { entityId: id }, bubbles: true, composed: true })));
    return b;
  }
  money(v) { return this.num.format(v); }
  date(iso) { return iso ? this.day.format(new Date(`${iso}T12:00:00`)).replace('.', '') : '—'; }
  css() { return ''; }
  titleText(t) { return t[this.constructor.metric]; }
  render() {
    if (!this._config || !this._hass) return;
    const lang = this._config.language || (this._hass.language?.startsWith('ru') ? 'ru' : 'en');
    const t = this.t = FD_TEXT[lang];
    this.lang = lang;
    this.num = new Intl.NumberFormat(lang === 'ru' ? 'ru-RU' : 'en-US', { maximumFractionDigits: 0 });
    this.day = new Intl.DateTimeFormat(lang === 'ru' ? 'ru-RU' : 'en-US', { day: 'numeric', month: 'short' });
    const root = this.shadowRoot; root.replaceChildren();
    this.el('style', FD_CSS + this.css(), null, root);
    const card = this.el('ha-card', null, this.constructor.metric, root);
    if (!this.constructor.ownTitle && this.show('title')) this.el('h2', this._config.title || this.titleText(t), null, card);
    this.draw(card, t);
  }
  /** The usual case: one sensor with the block in `data`. */
  draw(card, t) {
    const { id, state, multiple } = this.resolve();
    const data = state?.attributes?.data;
    if (!state) { this.el('div', multiple ? t.multiple : id ? `${t.missing}: ${id}` : t.noSensor, 'empty', card); return; }
    if (['unavailable', 'unknown'].includes(state.state) || data == null) { this.el('div', t.unavailable, 'empty', card); return; }
    this.body(card, data, t, id);
  }
}

/* 1. Overview: debit, credit, cushion, free — choose the tiles and their order. */
class FindashOverviewCard extends FindashCard {
  static metric = 'overview';
  static blocks = [['title', 'Заголовок', 'Title'], ['units', 'Валюта под числом', 'Currency under the number']];
  check(config) {
    if (config.columns != null && !['auto', '1', '2', '3', '4'].includes(String(config.columns))) throw new Error('columns: auto | 1 | 2 | 3 | 4');
    for (const key of FD_TILES) if (config[key] != null && typeof config[key] !== 'string') throw new Error(`${key}: expected Entity ID`);
    if (config.tiles != null && (!Array.isArray(config.tiles) || config.tiles.some(k => !FD_TILES.includes(k)))) throw new Error(`tiles: a list of ${FD_TILES.join(', ')}`);
  }
  getCardSize() { return 3; }
  css() { return `.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
    .tile{all:unset;box-sizing:border-box;display:flex;flex-direction:column;gap:10px;align-items:flex-start;min-width:0;padding:16px;border:1px solid var(--divider-color,#ddd);border-radius:12px;cursor:pointer}
    .tile:disabled{cursor:default}.tile .label{color:var(--secondary-text-color);font-size:13px}
    .tile .value{font-size:26px;font-weight:650;letter-spacing:-.5px;max-width:100%;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
    .unit{font-size:11px;color:var(--secondary-text-color)}.free{border-color:var(--primary-color,#498c81)}.free .value{color:var(--primary-color,#498c81)}
    .negative .value{color:var(--error-color,#db4437)}.error{font-size:12px;line-height:1.4;color:var(--secondary-text-color);overflow-wrap:anywhere}
    @container(min-width:650px){.grid.auto.n4{grid-template-columns:repeat(4,minmax(0,1fr))}.grid.auto.n3{grid-template-columns:repeat(3,minmax(0,1fr))}}
    @container(max-width:330px){.tile{padding:10px}.tile .value{font-size:22px}}`; }
  draw(card, t) {
    const tiles = this._config.tiles?.length ? this._config.tiles : FD_TILES;
    const grid = this.el('div', null, 'grid', card);
    const columns = String(this._config.columns || 'auto');
    if (columns === 'auto') grid.classList.add('auto', `n${tiles.length}`);
    else grid.style.gridTemplateColumns = `repeat(${columns},minmax(0,1fr))`;
    if (tiles.length === 1 && columns === 'auto') grid.style.gridTemplateColumns = '1fr';
    for (const key of tiles) {
      const explicit = this._config[key]?.trim();
      const { id, state, multiple } = explicit ? { id: explicit, state: this._hass.states[explicit] }
        : this.resolve(s => s.attributes.findash_metric === key);
      const tile = this.el('button', null, `tile ${key}`, grid); tile.type = 'button'; tile.title = t[`${key}Hint`];
      this.el('span', t[key], 'label', tile);
      const value = this.el('span', null, 'value', tile);
      const raw = state?.state;
      const num = raw == null || String(raw).trim() === '' ? NaN : Number(raw);
      const valid = !!state && !['unknown', 'unavailable'].includes(raw) && Number.isFinite(num);
      value.textContent = valid ? this.money(num) : '—';
      if (valid) {
        if (num < 0) tile.classList.add('negative');
        if (this.show('units')) this.el('span', state.attributes.unit_of_measurement || 'USD', 'unit', tile);
      } else {
        this.el('span', multiple ? t.multiple : !state ? `${t.missing}${id ? `: ${id}` : ''}` : ['unknown', 'unavailable'].includes(raw) ? t.tileUnavailable : t.invalid, 'error', tile);
      }
      tile.disabled = !state;
      if (state) tile.addEventListener('click', () => this.dispatchEvent(new CustomEvent('hass-more-info', { detail: { entityId: id }, bubbles: true, composed: true })));
    }
  }
}

/* 2. Money flow: plan / this month, the split bar, every part, the month-end forecast. */
class FindashMoneyFlowCard extends FindashCard {
  static metric = 'flow';
  static blocks = [['title', 'Заголовок', 'Title'], ['tabs', 'Переключатель План / Этот месяц', 'Plan / This month switch'],
    ['month', 'Месяц и валюта', 'Month and currency'], ['totals', 'Доход и платежи', 'Income and bills'],
    ['bar', 'Цветная полоса', 'Colour bar'], ['parts', 'Строки частей', 'Part rows'], ['rest', 'Итог', 'Bottom line'],
    ['forecast', 'Прогноз на конец месяца', 'Month-end forecast'], ['footer', 'Время расчёта', 'Calculated at']];
  static ownTitle = true;
  check(config) { if (config.view && !['plan', 'now'].includes(config.view)) throw new Error('view: plan | now'); }
  setConfig(config) { this._view = config.view || 'plan'; super.setConfig(config); }
  getCardSize() { return 6; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: 7, min_rows: 3 }; }
  static getStubConfig() { return {}; }
  css() { return `.top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
    .top h2{margin:0}.tabs{display:flex;gap:4px}
    .tabs button{font:inherit;font-size:12px;color:var(--secondary-text-color);background:transparent;border:1px solid var(--divider-color,#ccc);border-radius:16px;padding:7px 10px;cursor:pointer}
    .tabs button[aria-pressed=true]{background:var(--primary-color,#5187ba);color:var(--text-primary-color,#fff);border-color:transparent}
    .total{border-top:1px solid var(--divider-color,#ddd);padding-top:12px;font-weight:600}
    .flowbar{display:flex;height:18px;border-radius:5px;overflow:hidden;background:var(--secondary-background-color,#eee);margin:18px 0}.flowbar span{height:100%;flex-shrink:0}
    i.dot{display:inline-block;width:9px;height:9px;border-radius:2px;flex-shrink:0}
    .fc{margin-top:16px;padding-top:6px;border-top:1px solid var(--divider-color,#ddd)}footer{margin-top:16px}`; }
  draw(card, t) {
    const top = this.el('div', null, 'top', card);
    if (this.show('title')) this.el('h2', this._config.title || t.flow, null, top);
    if (this.show('tabs')) {
      const tabs = this.el('div', null, 'tabs', top);
      for (const mode of ['plan', 'now']) {
        const b = this.el('button', t[mode], null, tabs); b.type = 'button'; b.setAttribute('aria-pressed', String(this._view === mode));
        b.addEventListener('click', () => { this._view = mode; this.render(); this.shadowRoot.querySelector('.tabs button[aria-pressed=true]')?.focus(); });
      }
    }
    const { id, state, multiple } = this.resolve(s => s.attributes.flow?.plan && s.attributes.flow?.now);
    if (!state) {
      const ids = Object.keys(this._hass.states).filter(k => this._hass.states[k].attributes?.flow?.plan);
      this.el('div', id ? `${t.flowMissing}: ${id}` : multiple ? `${t.flowMultiple}: ${ids.join(', ')}` : t.flowNoSensor, 'empty', card);
      return;
    }
    if (['unavailable', 'unknown'].includes(state.state)) { this.el('div', t.unavailable, 'empty', card); return; }
    const f = state.attributes.flow?.[this._view];
    if (!f) { this.el('div', `${t.flowInvalid}: ${id}`, 'empty', card); return; }
    const row = (label, amount, cls = '', parent = card, color = null) => {
      const line = this.el('div', null, `row ${cls}`, parent), text = this.el('span', null, 'label', line);
      if (color) this.el('i', null, 'dot', text).style.background = color;
      text.append(document.createTextNode(label)); this.el('b', this.money(amount), amount < 0 ? 'negative' : '', line);
    };
    if (this.show('month')) this.el('div', `${state.attributes.month} · ${state.attributes.currency || 'USD'}`, 'muted', card);
    if (this.show('totals')) { row(t.income, f.income); row(t.mandatory, f.mandatory); row(t.left, f.left, 'total'); }
    const order = Object.keys(FD_FLOW_COLORS);
    const parts = [...f.parts].sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id));
    if (this.show('bar')) {
      const scale = Math.max(f.left, parts.reduce((sum, p) => sum + Math.max(p.amount, 0), 0), 1);
      const bar = this.el('div', null, 'flowbar', card); bar.setAttribute('role', 'img');
      bar.setAttribute('aria-label', parts.map(p => `${t[p.id]}: ${this.money(p.amount)}`).join(', '));
      for (const p of parts) if (p.amount > 0) {
        const seg = this.el('span', null, null, bar); seg.style.width = `${p.amount / scale * 100}%`;
        seg.style.background = FD_FLOW_COLORS[p.id]; seg.title = `${t[p.id]}: ${this.money(p.amount)}`;
      }
    }
    if (this.show('parts')) {
      for (const p of parts) if (p.amount !== 0 || p.id === 'prepay') row(t[p.id] || p.id, p.amount, '', card, FD_FLOW_COLORS[p.id]);
      if (!parts.some(p => p.amount)) this.el('div', t.emptyFlow, 'muted', card);
    }
    if (this.show('rest')) row(f.rest < 0 ? t.short : this._view === 'plan' ? t.rest : t.available, f.rest, 'total');
    if (this.show('forecast') && this._view === 'now' && f.end) {
      const box = this.el('div', null, 'fc', card);
      row(t.ahead, f.end.income_ahead, 'muted', box); row(t.bills, f.end.mandatory_ahead, 'muted', box);
      row(t.end, f.end.result, '', box); this.el('div', t.ifNothing, 'muted', box);
    }
    const stamp = new Date(state.attributes.generated_at);
    if (this.show('footer') && !Number.isNaN(stamp.getTime())) this.el('footer', `${t.updated}: ${stamp.toLocaleString(this.lang)}`, 'muted', card);
  }
}

/* 3. Today: the allowance, pocket money against the month, the piggy bank. */
class FindashTodayCard extends FindashCard {
  static metric = 'today';
  static blocks = [['title', 'Заголовок', 'Title'], ['allowance', '«Можно потратить сегодня»', 'Daily allowance'],
    ['days', 'Дней до конца месяца', 'Days left'], ['pocket', 'Полоска карманных', 'Pocket money bar'],
    ['month_mark', 'Отметка «сколько месяца прошло»', 'Month-elapsed mark'], ['piggy', 'Копилка', 'Piggy bank']];
  getGridOptions() { return { columns: 6, min_columns: 4, rows: 3, min_rows: 1 }; }
  css() { return `.big{font-size:40px;font-weight:700;letter-spacing:-1px;font-variant-numeric:tabular-nums;color:var(--success-color,#43a047);line-height:1.1}
    .big.zero{color:var(--error-color,#db4437)}.pocket{margin-top:14px}`; }
  body(card, d, t, id) {
    if (this.show('allowance') || this.show('days')) {
      const top = this.tap(card, id);
      if (this.show('allowance')) {
        this.el('div', t.canSpend, 'muted', top);
        this.el('div', this.money(d.can_spend), d.can_spend <= 0 ? 'big zero' : 'big', top);
      }
      if (this.show('days')) this.el('div', t.daysLeft(d.days_left), 'muted', top);
    }
    if (this.show('pocket')) {
      const p = d.pocket || {};
      const box = this.el('div', null, 'pocket', card);
      const row = this.el('div', null, 'row', box);
      this.el('span', t.pocket, null, row);
      this.el('b', t.spentOf(this.money(p.spent), this.money(p.monthly)), p.left < 0 ? 'negative' : '', row);
      const used = p.monthly ? p.spent / p.monthly : (p.spent ? 1 : 0);
      const color = used > 1 ? FD_STATE.full : used > d.elapsed + 0.15 ? FD_STATE.warn : FD_STATE.ok;
      this.bar(box, used, color, this.show('month_mark') ? d.elapsed : null);
    }
    if (this.show('piggy')) {
      const row = this.el('div', null, 'row', card);
      this.el('span', t.piggy, 'muted', row); this.el('b', this.money(d.piggy), null, row);
    }
  }
}

/* 4. Limits: every envelope as on the website — choose which, in which order. */
class FindashLimitsCard extends FindashCard {
  static metric = 'limits';
  static blocks = [['title', 'Заголовок', 'Title'], ['values', 'Суммы и проценты', 'Amounts and percent'],
    ['bars', 'Полоски', 'Bars'], ['month_mark', 'Отметка «сколько месяца прошло»', 'Month-elapsed mark'],
    ['carry', 'Перенос с прошлого месяца', 'Carry-over'], ['stop', '«Хватит в этом месяце»', '"Enough for this month"']];
  check(config) {
    if (config.limits != null && !Array.isArray(config.limits)) throw new Error('limits: a list of ids, e.g. [pocket, food]');
    if (config.columns != null && !['auto', '1', '2'].includes(String(config.columns))) throw new Error('columns: auto | 1 | 2');
  }
  getCardSize() { return 6; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: 6, min_rows: 2 }; }
  css() { return `.grid{display:grid;gap:0 24px}@container(min-width:600px){.grid.auto{grid-template-columns:1fr 1fr}}
    button.tap.lim{margin:0 0 14px}.lim .row{margin:0 0 2px}.stop{color:var(--error-color,#db4437);font-size:12px;font-weight:600}
    .chip{font-size:11px;color:var(--secondary-text-color);margin-left:6px}`; }
  body(card, limits, t, id) {
    const byId = Object.fromEntries(limits.map(b => [b.id, b]));
    let shown = this._config.limits?.length ? this._config.limits.map(String).filter(k => byId[k]).map(k => byId[k]) : limits;
    if (this._config.hide_pocket) shown = shown.filter(b => b.id !== 'pocket');
    if (this._config.only_problems) shown = shown.filter(b => b.state === 'warn' || b.state === 'full');
    if (!shown.length) { this.el('div', this._config.only_problems && limits.length ? t.allGood : t.noLimits, 'empty', card); return; }
    const elapsed = this.show('month_mark') ? this.elapsed() : null;
    const grid = this.el('div', null, 'grid', card);
    const columns = String(this._config.columns || 'auto');
    if (columns === 'auto') grid.classList.add('auto'); else grid.style.gridTemplateColumns = `repeat(${columns},minmax(0,1fr))`;
    for (const b of shown) {
      const lim = this.tap(grid, id, 'lim');
      const row = this.el('div', null, 'row', lim);
      const name = this.el('span', b.name, null, row);
      if (this.show('carry') && b.carry) this.el('span', `${t.carry} ${b.carry > 0 ? '+' : '−'}${this.money(Math.abs(b.carry))}`, 'chip', name);
      if (this.show('values')) this.el('b', b.limit ? `${t.spentOf(this.money(b.spent), this.money(b.limit))} · ${Math.round(b.pct * 100)}%` : `${this.money(b.spent)} · ${t.noLimit}`, null, row);
      if (this.show('bars')) this.bar(lim, b.state === 'none' ? 1 : b.pct, FD_STATE[b.state] || FD_STATE.none, elapsed);
      if (this.show('stop') && b.state === 'full') this.el('div', t.over, 'stop', lim);
    }
  }
  elapsed() {  // the month mark comes from the Today sensor when it exists
    const today = Object.values(this._hass.states).find(s => s.attributes?.findash_metric === 'today' && s.attributes.data);
    return today ? today.attributes.data.elapsed : null;
  }
}

/* 5. Forecast: the lowest point, a chart, payday and the next payment. */
class FindashForecastCard extends FindashCard {
  static metric = 'forecast';
  static blocks = [['title', 'Заголовок', 'Title'], ['summary', 'Минимум и дата', 'Lowest balance and date'],
    ['warning', 'Предупреждение о минусе', 'Below-zero warning'], ['chart', 'График', 'Chart'],
    ['income', 'Зарплата', 'Payday'], ['payment', 'Ближайший платёж', 'Next payment']];
  check(config) { if (config.days != null && ![7, 14, 30].includes(Number(config.days))) throw new Error('days: 7 | 14 | 30'); }
  getCardSize() { return 5; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: 5, min_rows: 2 }; }
  css() { return `button.tap.head{display:flex;flex-wrap:wrap;gap:4px 16px;align-items:flex-end}
    .big{font-size:32px;font-weight:700;letter-spacing:-.8px;font-variant-numeric:tabular-nums}
    svg{display:block;width:100%;height:90px;margin:12px 0 6px;overflow:visible}
    .warn{background:color-mix(in srgb,var(--error-color,#db4437) 14%,transparent);border-radius:8px;padding:8px 10px;font-size:13px;margin:8px 0}`; }
  titleText(t) { return `${t.forecast} · ${Number(this._config.days || 30)} ${t.days}`; }
  body(card, f, t, id) {
    const n = Number(this._config.days || 30);
    const points = (f.points || []).slice(0, n + 1);
    const full = n >= 30 || points.length < 2;  // the server's own low point for the whole window
    const low = full ? f.min.balance : Math.min(...points);
    const lowDate = full ? f.min.date : this.shift(f.first_date, points.indexOf(low));
    if (this.show('summary')) {
      const head = this.tap(card, id, 'head');
      const left = this.el('div', null, null, head);
      this.el('div', t.min, 'muted', left);
      this.el('div', this.money(low), low < 0 ? 'big negative' : 'big', left);
      this.el('div', `${this.date(lowDate)} · ${t.nowShort} ${this.money(f.start)} · ${t.after(n)} ${this.money(points.at(-1) ?? f.end)}`, 'muted', head);
    }
    if (this.show('warning') && low < 0) this.el('div', t.low, 'warn', card);
    if (this.show('chart')) this.spark(card, points, low);
    const end = this.shift(f.first_date, n);
    const within = item => item && (!end || item.date <= end);
    if (this.show('income')) this.line(card, t.nextIncome, within(f.next_income) ? f.next_income : null, '+');
    if (this.show('payment')) this.line(card, t.nextPayment, within(f.next_payment) ? f.next_payment : null, '−');
  }
  shift(iso, days) {
    if (!iso) return null;
    const d = new Date(`${iso}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + days);
    return d.toISOString().slice(0, 10);
  }
  line(card, label, item, sign) {
    const row = this.el('div', null, 'row', card);
    this.el('span', item?.what ? `${label} · ${item.what}` : label, null, row);
    this.el('b', item ? `${this.date(item.date)} · ${sign}${this.money(item.amount)}` : '—', null, row);
  }
  spark(card, points, min) {
    if (points.length < 2) return;
    const NS = 'http://www.w3.org/2000/svg', W = 300, H = 90, pad = 4;
    const low = Math.min(...points, ...(min < 0 ? [0] : [])), high = Math.max(...points);
    const air = (high - low) * 0.15 || 1, lo = low - air, hi = high + air;
    const x = i => (i / (points.length - 1)) * W, y = v => H - pad - ((v - lo) / (hi - lo)) * (H - 2 * pad);
    const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('preserveAspectRatio', 'none'); svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', points.map(v => this.money(v)).join(', '));
    const path = (d, stroke, width, dash) => {
      const p = document.createElementNS(NS, 'path'); p.setAttribute('d', d); p.setAttribute('fill', 'none');
      p.setAttribute('stroke', stroke); p.setAttribute('stroke-width', width); p.setAttribute('vector-effect', 'non-scaling-stroke');
      p.setAttribute('stroke-linejoin', 'round'); if (dash) p.setAttribute('stroke-dasharray', dash); svg.append(p);
    };
    if (lo < 0) path(`M0 ${y(0)} H${W}`, 'var(--error-color,#db4437)', 1, '4 4');
    path(points.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join(' '),
      min < 0 ? 'var(--error-color,#db4437)' : 'var(--primary-color,#03a9f4)', 2);
    card.append(svg);
  }
}

/* 6. Game: hero, XP, streak, quests, the mortgage dragon, achievements. */
class FindashGameCard extends FindashCard {
  static metric = 'game';
  static blocks = [['title', 'Заголовок', 'Title'], ['hero', 'Герой и опыт', 'Hero and XP'], ['stats', 'Серия и копилка', 'Streak and piggy bank'],
    ['quests', 'Задания на сегодня', "Today's quests"], ['boss', 'Дракон ипотеки', 'Mortgage dragon'],
    ['achievements', 'Достижения', 'Achievements'], ['locked', 'Ещё не полученные достижения', 'Locked achievements']];
  show(key) { return key === 'locked' ? this._config.show_locked === true : super.show(key); }
  getCardSize() { return 6; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: 6, min_rows: 2 }; }
  css() { return `ha-card.game{background:radial-gradient(ellipse at top,#2a2116 0%,#14100b 75%);color:#f1e3c0;border:1px solid #6b5427}
    .game h2{font-family:Georgia,'Times New Roman',serif;color:#e8c062;letter-spacing:.5px}
    .game .muted,.game .empty{color:#b9a780}
    button.tap.hero{display:flex;gap:14px;align-items:center;margin-bottom:12px}
    .portrait{flex:none;width:56px;height:56px;border-radius:50%;display:grid;place-items:center;font:700 24px Georgia,serif;color:#ffd76a;
      background:radial-gradient(circle at 35% 30%,#5a4422,#1d150b 70%);box-shadow:0 0 0 3px #b8892f,0 0 12px rgba(232,192,98,.35)}
    .info{flex:1;min-width:0}.name{font:700 16px Georgia,serif;color:#ffd76a}
    .xp{position:relative;height:14px;border-radius:3px;background:#0b0905;box-shadow:inset 0 0 0 1px #5c4a26;margin:6px 0;overflow:hidden}
    .xp i{display:block;height:100%;background:linear-gradient(180deg,#b45cff,#6a1fb8)}
    .xp span{position:absolute;inset:0;display:grid;place-items:center;font-size:10px;color:#fff;text-shadow:0 1px 2px #000}
    .stats{display:flex;flex-wrap:wrap;gap:2px 14px;font-size:13px;color:#d9c8a0;margin:4px 0}.stats b{color:#ffd76a}
    h3{font:600 13px Georgia,serif;color:#e8c062;margin:14px 0 6px}
    .quest{display:grid;grid-template-columns:20px 1fr auto;gap:6px;align-items:center;font-size:13px;margin:4px 0}
    .quest .q{color:#ffd100;font-weight:800;text-align:center}.quest.done .n{color:#9a8a6a;text-decoration:line-through}
    .quest .x{color:#c58cff;font-size:12px;white-space:nowrap}
    .boss{margin-top:12px;padding:8px 10px;border-radius:6px;background:linear-gradient(90deg,rgba(120,20,10,.35),rgba(0,0,0,.2));box-shadow:inset 0 0 0 1px #6b2a1a}
    .boss .row{margin:0 0 6px;font-size:13px}.boss .row span{font:700 13px Georgia,serif;color:#ff7a59}
    .hp{height:12px;border-radius:3px;background:#1a0705;overflow:hidden}.hp i{display:block;height:100%;background:linear-gradient(180deg,#e8412b,#8f150b)}
    .chips{display:flex;flex-wrap:wrap;gap:5px}.chip{font-size:11px;padding:3px 7px;border-radius:4px;background:#0e0b07;box-shadow:inset 0 0 0 1px currentColor}
    .chip.locked{color:#6b6253!important;opacity:.7}`; }
  body(card, g, t, id) {
    if (this.show('hero')) {
      const hero = this.tap(card, id, 'hero');
      this.el('div', String(g.level), 'portrait', hero).title = t.level;
      const info = this.el('div', null, 'info', hero);
      this.el('div', g.title || '', 'name', info);
      const xp = this.el('div', null, 'xp', info);
      const top = g.level >= 60;
      this.el('i', null, null, xp).style.width = `${top ? 100 : Math.min(g.level_xp / (g.level_need || 1), 1) * 100}%`;
      this.el('span', top ? t.maxLevel : `${g.level_xp} / ${g.level_need} ${t.xp}`, null, xp);
      if (this.show('stats')) this.stats(info, g, t);
    } else if (this.show('stats')) this.stats(card, g, t);
    if (this.show('quests') && g.quests?.length) {
      this.el('h3', t.quests, null, card);
      for (const q of g.quests) {
        const row = this.el('div', null, q.done ? 'quest done' : 'quest', card);
        this.el('span', q.done ? '✓' : '!', 'q', row); this.el('span', q.name, 'n', row); this.el('span', `+${q.xp}`, 'x', row);
      }
    }
    if (this.show('boss') && g.boss) {
      const boss = this.el('div', null, 'boss', card);
      const row = this.el('div', null, 'row', boss);
      this.el('span', g.boss.name || '', null, row);
      this.el('b', `${t.hp} ${this.money(g.boss.hp)} / ${this.money(g.boss.max_hp)}`, 'muted', row);
      this.el('i', null, null, this.el('div', null, 'hp', boss)).style.width = `${Math.max(Math.min(g.boss.pct, 1), 0) * 100}%`;
      if (g.boss.hits) this.el('div', t.hits(g.boss.hits), 'muted', boss);
    }
    const all = g.achievements || [];
    if (this.show('achievements') && all.length) {
      const earned = all.filter(a => a.earned);
      this.el('h3', `${t.achievements} · ${earned.length} / ${all.length}`, null, card);
      const chips = this.el('div', null, 'chips', card);
      for (const a of this.show('locked') ? all : earned) {
        const chip = this.el('span', a.name, a.earned ? 'chip' : 'chip locked', chips);
        chip.style.color = FD_RARITY[a.rarity] || FD_RARITY.common;
      }
    }
  }
  stats(parent, g, t) {
    const stats = this.el('div', null, 'stats', parent);
    const stat = (label, value) => { const s = this.el('span', `${label} `, null, stats); this.el('b', value, null, s); };
    stat(`${t.streak}:`, `${g.streak} ${t.days}`); stat(`${t.best}:`, String(g.best_streak)); stat('🪙', this.money(g.piggy));
  }
}

/* ---------------------------------------------------------------------------------------- */
/** One visual editor for all six cards: entity, title, language, card options, a checkbox
    per block, and for lists (tiles, limits) a checkbox per item. Unknown keys (grid_options,
    visibility...) are kept. */
class FindashCardEditor extends HTMLElement {
  constructor() { super(); this.attachShadow({ mode: 'open' }); }
  set hass(hass) { const first = !this._hass; this._hass = hass; if (first) this.render(); }
  setConfig(config) { this._config = { ...config }; this.render(); }
  emit(config) {
    this._config = config;
    this.dispatchEvent(new CustomEvent('config-changed', { detail: { config }, bubbles: true, composed: true }));
  }
  set(key, value) {
    const config = { ...this._config };
    if (value === undefined || value === '' || (Array.isArray(value) && !value.length)) delete config[key]; else config[key] = value;
    this.emit(config);
  }
  render() {
    if (!this._config || !this.card) return;
    const ru = (this._config.language || this._hass?.language || 'en').startsWith('ru');
    const L = (r, e) => (ru ? r : e);
    const root = this.shadowRoot; root.replaceChildren();
    const style = document.createElement('style');
    style.textContent = `label{display:block;margin:14px 0;color:var(--primary-text-color)}
      input[type=text],select{display:block;box-sizing:border-box;width:100%;margin-top:8px;padding:12px;font:inherit;color:var(--primary-text-color);background:var(--card-background-color,#fff);border:1px solid var(--divider-color,#aaa);border-radius:6px}
      fieldset{border:1px solid var(--divider-color,#aaa);border-radius:8px;margin:16px 0;padding:8px 12px}legend{padding:0 6px;color:var(--secondary-text-color)}
      label.check{display:flex;align-items:center;gap:10px;margin:8px 0}label.check input{width:18px;height:18px;margin:0}
      p{line-height:1.5;color:var(--secondary-text-color)}`;
    root.append(style);
    const text = (key, caption) => {
      const label = document.createElement('label'); label.textContent = caption;
      const input = document.createElement('input'); input.type = 'text'; input.name = key; input.setAttribute('aria-label', caption);
      input.value = this._config[key] ?? '';
      input.addEventListener('change', () => this.set(key, input.value.trim() || undefined));
      label.append(input); root.append(label);
    };
    const select = (key, caption, options, parse = v => v) => {
      const label = document.createElement('label'); label.textContent = caption;
      const input = document.createElement('select'); input.name = key; input.setAttribute('aria-label', caption);
      for (const [value, title] of options) { const o = document.createElement('option'); o.value = value; o.textContent = title; input.append(o); }
      input.value = this._config[key] == null ? '' : String(this._config[key]);
      input.addEventListener('change', () => this.set(key, input.value === '' ? undefined : parse(input.value)));
      label.append(input); root.append(label);
    };
    const checks = (legend, items) => {
      const box = document.createElement('fieldset'); const lg = document.createElement('legend'); lg.textContent = legend; box.append(lg);
      for (const [caption, checked, onChange] of items) {
        const label = document.createElement('label'); label.className = 'check';
        const input = document.createElement('input'); input.type = 'checkbox'; input.checked = checked; input.setAttribute('aria-label', caption);
        input.addEventListener('change', () => onChange(input.checked));
        label.append(input, document.createTextNode(caption)); box.append(label);
      }
      root.append(box);
    };
    const card = this.card, metric = card.metric;
    if (metric !== 'overview') text('entity', L('Сенсор (пусто — найти автоматически)', 'Entity (leave blank to detect automatically)'));
    text('title', L('Заголовок (необязательно)', 'Title (optional)'));
    select('language', L('Язык', 'Language'), [['', L('Как в Home Assistant', 'Home Assistant language')], ['ru', 'Русский'], ['en', 'English']]);
    if (metric === 'overview') {
      select('columns', L('Колонки', 'Tile columns'), [['', L('Автоматически', 'Automatic')], ['1', '1'], ['2', '2'], ['3', '3'], ['4', '4']]);
      const chosen = this._config.tiles?.length ? this._config.tiles : FD_TILES;
      checks(L('Плитки', 'Tiles'), FD_TILES.map(k => [FD_TEXT[ru ? 'ru' : 'en'][k], chosen.includes(k), on => {
        const next = FD_TILES.filter(x => (x === k ? on : chosen.includes(x)));
        this.set('tiles', next.length === FD_TILES.length ? undefined : next);
        this.render();
      }]));
      for (const k of FD_TILES) text(k, `${FD_TEXT.en[k]} entity (${L('пусто — автоматически', 'automatic if blank')})`);
    }
    if (metric === 'flow') select('view', L('Вид по умолчанию', 'Default view'), [['', L('План', 'Plan')], ['now', L('Этот месяц', 'This month')]]);
    if (metric === 'limits') {
      select('columns', L('Колонки', 'Columns'), [['', L('Автоматически', 'Automatic')], ['1', '1'], ['2', '2']]);
      select('only_problems', L('Какие показывать', 'Which to show'), [['', L('Все', 'All')], ['true', L('Только жёлтые и красные', 'Only warn and full')]], v => v === 'true');
      const states = this._hass?.states || {};
      const sensor = Object.values(states).find(s => s.attributes?.findash_metric === 'limits' && Array.isArray(s.attributes.data));
      const all = sensor ? sensor.attributes.data.map(b => [b.id, b.name]) : [];
      if (all.length) {
        const chosen = this._config.limits?.length ? this._config.limits : all.map(([k]) => k);
        checks(L('Полоски', 'Bars'), all.map(([k, name]) => [name, chosen.includes(k), on => {
          const next = all.map(([x]) => x).filter(x => (x === k ? on : chosen.includes(x)));
          this.set('limits', next.length === all.length ? undefined : next);
          this.render();
        }]));
      }
    }
    if (metric === 'forecast') select('days', L('Период', 'Window'), [['', '30'], ['14', '14'], ['7', '7']], Number);
    checks(L('Показывать', 'Show'), card.blocks.map(([key, r, e]) => {
      const on = key === 'locked' ? this._config.show_locked === true : this._config[`show_${key}`] !== false;
      return [L(r, e), on, value => this.set(`show_${key}`, key === 'locked' ? (value || undefined) : (value ? undefined : false))];
    }));
    const hint = document.createElement('p');
    hint.textContent = L('Размер карточки — во вкладке Layout (в виде Sections). Порядок полосок и плиток можно задать списком в YAML.',
      'Resize in the Layout tab (Sections view). The order of bars and tiles can be set as a list in YAML.');
    root.append(hint);
  }
}

if (!customElements.get('findash-card-editor')) customElements.define('findash-card-editor', FindashCardEditor);
window.customCards = window.customCards || [];
for (const [tag, cls, name, description] of [
  ['findash-overview-card', FindashOverviewCard, 'Findash — Overview', 'Дебит, кредит, подушка, свободно'],
  ['findash-money-flow-card', FindashMoneyFlowCard, 'Findash — Money flow', 'Куда идут деньги: план и этот месяц'],
  ['findash-today-card', FindashTodayCard, 'Findash — Today', 'Сегодня можно, карманные и копилка'],
  ['findash-limits-card', FindashLimitsCard, 'Findash — Limits', 'Лимиты на месяц, как на сайте'],
  ['findash-forecast-card', FindashForecastCard, 'Findash — Forecast', 'Прогноз денег на 30 дней'],
  ['findash-game-card', FindashGameCard, 'Findash — Game', 'Герой, задания и дракон ипотеки'],
]) {
  if (!customElements.get(tag)) customElements.define(tag, cls);
  if (!window.customCards.some(c => c.type === tag)) window.customCards.push({ type: tag, name, description, preview: true });
}
console.info(`%cFindash cards ${FD_VERSION}`, 'color:#489b83;font-weight:600');
