/* Sound Vibration Sanctuary: the RSVP calendar.
   Dates, times, prices and spots come from data/schedule.json (edit that file, not this one).
   No payment is taken online: guests RSVP here and pay in person.
   Where RSVPs go is set in data/config.json: a free form service (Web3Forms key or Formspree link in "rsvpFormKey"),
   else an email to "rsvpEmail", else (both empty, as now) a ready-made text message to her phone. The rules below are plain functions so tests can check them. */
(function (root) {
  'use strict';

  var B = {};
  B.DOG_PAIR_MAX_LB = 30;   // two dogs are welcome when they weigh this much or less together; one dog: any size
  B.AZ_OFFSET_HOURS = 7;    // Arizona is UTC-7 all year (no daylight saving)

  B.pad = function (n) { return (n < 10 ? '0' : '') + n; };

  // When the session starts, as a moment in time (its date and start are Arizona time)
  B.startsAt = function (s) {
    var d = s.date.split('-'), t = s.start.split(':');
    return Date.UTC(+d[0], +d[1] - 1, +d[2], +t[0] + B.AZ_OFFSET_HOURS, +t[1]);
  };
  B.isPast = function (s, now) { return B.startsAt(s) <= (now == null ? Date.now() : now); };

  B.spotsLeft = function (s) { return Math.max(0, (s.capacity || 0) - (s.booked || 0)); };
  B.dogSpotsLeft = function (s) { return s.dogs ? Math.max(0, (s.dogCapacity || 0) - (s.dogsBooked || 0)) : 0; };
  B.isFull = function (s) { return B.spotsLeft(s) <= 0; };
  B.isOpen = function (s, now) { return !B.isPast(s, now) && !B.isFull(s); };

  B.time12 = function (hhmm) {
    var p = hhmm.split(':'), h = +p[0], m = p[1];
    return (h % 12 || 12) + ':' + m + ' ' + (h < 12 ? 'AM' : 'PM');
  };
  var DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  B.MONTHS = MONTHS;
  B.dateParts = function (iso) { var d = iso.split('-'); return { y: +d[0], m: +d[1], d: +d[2] }; };
  B.weekday = function (iso) { var p = B.dateParts(iso); return DAYS[new Date(Date.UTC(p.y, p.m - 1, p.d)).getUTCDay()]; };
  B.longDate = function (iso) { var p = B.dateParts(iso); return B.weekday(iso) + ', ' + MONTHS[p.m - 1] + ' ' + p.d; };
  B.label = function (s) { return B.longDate(s.date) + ', ' + B.time12(s.start) + ': ' + s.title; };

  // The dog rule: one dog of any weight, OR two dogs that weigh 30 lb or less together. Returns '' when fine.
  B.dogRule = function (count, weights) {
    count = +count || 0;
    if (count === 0 || count === 1) return '';
    if (count > 2) return 'Up to two dogs per RSVP, please.';
    var a = parseFloat(weights && weights[0]), b = parseFloat(weights && weights[1]);
    if (!(a > 0) || !(b > 0)) return 'Please enter both dogs’ weights in pounds.';
    var total = Math.round((a + b) * 10) / 10;
    if (total > B.DOG_PAIR_MAX_LB) {
      return 'Two dogs are welcome when they weigh ' + B.DOG_PAIR_MAX_LB + ' lb or less together (yours come to ' + total +
        ' lb). One dog of any size is always welcome.';
    }
    return '';
  };

  // Checks a whole RSVP against the session. Returns a list of {field, message}; empty means it can be sent.
  B.check = function (s, r) {
    var errs = [];
    var add = function (field, message) { errs.push({ field: field, message: message }); };
    if (!s) { add('slot', 'Please pick a date and time on the calendar.'); return errs; }
    if (B.isPast(s, r.now)) add('slot', 'That session has already started. Please pick another date.');
    else if (B.isFull(s)) add('slot', 'That session is full. Please pick another date, or text us to join the waiting list.');
    if (!(r.name || '').trim()) add('name', 'Please tell us your name.');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((r.email || '').trim())) add('email', 'Please enter your email address.');
    if (((r.phone || '').match(/\d/g) || []).length < 10) add('phone', 'Please enter your phone number (10 digits).');
    var people = Math.floor(+r.people);
    var left = B.spotsLeft(s);
    if (!(people >= 1)) add('people', 'How many people are coming (including you)?');
    else if (left > 0 && people > left) add('people', 'Only ' + left + (left === 1 ? ' spot is' : ' spots are') + ' left for this session.');
    var dogs = +r.dogs || 0;
    if (dogs > 0) {
      if (!s.dogs) add('dogs', 'Dogs are welcome at the Sunday sessions. This one is people only.');
      else if (dogs > B.dogSpotsLeft(s)) {
        var dl = B.dogSpotsLeft(s);
        add('dogs', dl ? 'Only ' + dl + (dl === 1 ? ' dog spot is' : ' dog spots are') + ' left for this session.' : 'The dog spots for this session are taken.');
      } else {
        var rule = B.dogRule(dogs, r.dogWeights || []);
        if (rule) add('dogs', rule);
      }
    }
    return errs;
  };

  B.total = function (s, people) { return (s ? s.price : 0) * (Math.max(1, Math.floor(+people) || 1)); };

  B.summary = function (s, r) {
    var lines = [
      'RSVP: ' + B.label(s),
      'Name: ' + r.name,
      'Email: ' + r.email,
      'Phone: ' + r.phone,
      'People: ' + r.people + ' (' + r.people + ' x $' + s.price + ' = $' + B.total(s, r.people) + ', paid in person)'
    ];
    var dogs = +r.dogs || 0;
    if (s.dogs) {
      lines.push('Dogs: ' + (dogs ? dogs + (dogs === 1 ? ' dog' : ' dogs') : 'none') +
        (dogs && (r.dogWeights || []).filter(Boolean).length ? ' (' + r.dogWeights.slice(0, dogs).filter(Boolean).join(' lb, ') + ' lb)' : ''));
    }
    if ((r.notes || '').trim()) lines.push('Notes: ' + r.notes.trim());
    return lines.join('\n');
  };

  B.smsLink = function (phone, body) { return 'sms:+1' + String(phone).replace(/\D/g, '').slice(-10) + '?&body=' + encodeURIComponent(body); };

  // Where an RSVP goes: a Web3Forms access key, a form link (Formspree or any service that takes JSON), or nothing yet.
  B.endpoint = function (form) {
    form = (form || '').trim();
    if (!form) return null;
    if (/^https:\/\//i.test(form)) return { url: form, key: null };
    return { url: 'https://api.web3forms.com/submit', key: form };
  };

  // Where RSVPs go is set in one place, data/config.json (rsvpEmail, rsvpFormKey). Older copies of schedule.json had
  // "email"/"form" lines; those still count when config.json leaves a value empty. Anything that isn't a real-looking
  // address is ignored, so a note left in the field can't become a broken mailto.
  B.settings = function (schedule, config) {
    schedule = schedule || {}; config = config || {};
    var email = String(config.rsvpEmail || schedule.email || '').trim();
    return {
      email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ? email : '',
      form: String(config.rsvpFormKey || schedule.form || '').trim()
    };
  };

  if (typeof module !== 'undefined' && module.exports) { module.exports = B; }
  if (typeof document === 'undefined') return;

  // ------------------------------------------------------------------------------------------------ the page
  var cal = document.getElementById('cal');
  var form = document.getElementById('rsvp-form');
  if (!cal || !form) return;

  var data = null, view = null, picked = null;
  var $ = function (id) { return document.getElementById(id); };
  var slotSel = $('r-slot'), peopleIn = $('r-people'), dogBox = $('r-dogbox'), weightsBox = $('r-weights');
  var dogNote = $('r-dognote'), totalOut = $('r-total'), statusEl = form.querySelector('.form-status');
  var byId = function (id) { return (data ? data.sessions : []).filter(function (s) { return s.id === id; })[0] || null; };
  var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  function spotsText(s) {
    if (B.isPast(s)) return 'This session has passed';
    var left = B.spotsLeft(s);
    if (!left) return 'Full';
    var t = left + ' of ' + s.capacity + ' spots open';
    if (s.dogs) t += ' · ' + B.dogSpotsLeft(s) + ' of ' + s.dogCapacity + ' dog spots';
    return t;
  }

  function renderMonth() {
    var y = view.y, m = view.m;
    var first = new Date(Date.UTC(y, m - 1, 1)).getUTCDay();
    var days = new Date(Date.UTC(y, m, 0)).getUTCDate();
    var key = y + '-' + B.pad(m) + '-';
    var months = monthsWithSessions();
    var idx = months.indexOf(y * 12 + m);
    var html = '<div class="cal-head"><button type="button" class="cal-nav" data-move="-1" aria-label="Previous month"' +
      (idx <= 0 ? ' disabled' : '') + '>‹</button><h3 id="cal-month" aria-live="polite">' + MONTHS[m - 1] + ' ' + y +
      '</h3><button type="button" class="cal-nav" data-move="1" aria-label="Next month"' + (idx >= months.length - 1 ? ' disabled' : '') +
      '>›</button></div><div class="cal-grid" role="grid" aria-labelledby="cal-month"><div class="cal-row cal-week" role="row">';
    ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(function (d, i) {
      html += '<span role="columnheader" aria-label="' + DAYS[i] + '">' + d + '</span>';
    });
    html += '</div><div class="cal-row" role="row">';
    for (var i = 0; i < first; i++) html += '<span class="cal-day is-blank" role="gridcell"></span>';
    for (var d = 1; d <= days; d++) {
      var iso = key + B.pad(d);
      var list = data.sessions.filter(function (s) { return s.date === iso; });
      if ((first + d - 1) % 7 === 0 && d !== 1) html += '</div><div class="cal-row" role="row">';
      if (!list.length) { html += '<span class="cal-day" role="gridcell">' + d + '</span>'; continue; }
      var open = list.some(function (s) { return B.isOpen(s); });
      var past = list.every(function (s) { return B.isPast(s); });
      var cls = 'cal-day has-session' + (open ? ' is-open' : past ? ' is-past' : ' is-full') + (list[0].dogs ? ' is-dogs' : '') +
        (picked && picked.date === iso ? ' is-picked' : '');
      var al = B.longDate(iso) + ': ' + list.map(function (s) { return B.time12(s.start) + ' ' + s.title + ', ' + spotsText(s); }).join('; ');
      html += '<span role="gridcell"><button type="button" class="' + cls + '" data-day="' + iso + '" aria-label="' + esc(al) + '"' +
        (picked && picked.date === iso ? ' aria-pressed="true"' : ' aria-pressed="false"') + '>' + d + '<i aria-hidden="true"></i></button></span>';
    }
    var cells = first + days;
    while (cells % 7) { html += '<span class="cal-day is-blank" role="gridcell"></span>'; cells++; }
    html += '</div></div>';
    $('cal-month-box').innerHTML = html;
  }

  function renderSlots(iso) {
    var box = $('cal-slots');
    var list = iso ? data.sessions.filter(function (s) { return s.date === iso; }) : upcoming();
    var head = iso ? B.longDate(iso) : 'Coming up';
    if (!list.length) { box.innerHTML = '<p class="cal-empty">No sessions are scheduled right now. Text ' + esc(data.phone) + ' to ask about the next ones.</p>'; return; }
    var html = '<h3 class="slots-title">' + esc(head) + '</h3><ul class="slot-list">';
    list.forEach(function (s) {
      var left = B.spotsLeft(s), open = B.isOpen(s);
      var pct = s.capacity ? Math.round(100 * (s.capacity - left) / s.capacity) : 100;
      html += '<li class="slot' + (open ? '' : ' is-closed') + (picked && picked.id === s.id ? ' is-picked' : '') + '">' +
        '<div class="slot-main"><span class="slot-when">' + esc((iso ? '' : B.longDate(s.date) + ' · ') + B.time12(s.start) + ' to ' + B.time12(s.end)) + '</span>' +
        '<strong class="slot-title">' + esc(s.title) + '</strong>' +
        '<span class="slot-meta">$' + s.price + ' per person' + (s.dogs ? ' · dogs welcome, free' : '') + '</span>' +
        '<span class="slot-spots">' + esc(spotsText(s)) + '</span>' +
        '<span class="meter" aria-hidden="true"><span style="width:' + pct + '%"></span></span></div>' +
        (open ? '<button type="button" class="btn btn-outline btn-sm" data-pick="' + esc(s.id) + '">' + (picked && picked.id === s.id ? 'Chosen' : 'RSVP') + '</button>'
          : '<span class="slot-tag">' + (B.isPast(s) ? 'Past' : 'Full') + '</span>') + '</li>';
    });
    box.innerHTML = html + '</ul>';
  }

  function upcoming() { return data.sessions.filter(function (s) { return !B.isPast(s); }).slice(0, 6); }
  function monthsWithSessions() {
    var set = {};
    data.sessions.forEach(function (s) { var p = B.dateParts(s.date); set[p.y * 12 + p.m] = 1; });
    return Object.keys(set).map(Number).sort(function (a, b) { return a - b; });
  }

  function fillSelect() {
    var keep = slotSel.value;
    slotSel.innerHTML = '<option value="">Pick a date and time</option>';
    data.sessions.forEach(function (s) {
      if (B.isPast(s)) return;
      var o = document.createElement('option');
      o.value = s.id;
      o.textContent = B.label(s) + (B.isFull(s) ? ' (full)' : ' (' + B.spotsLeft(s) + ' spots open)');
      o.disabled = B.isFull(s);
      slotSel.appendChild(o);
    });
    slotSel.value = keep;
  }

  function dogCount() { var c = form.querySelector('input[name=dogs]:checked'); return c ? +c.value : 0; }

  function syncForm() {
    var s = picked;
    var allowDogs = !!(s && s.dogs);
    dogBox.disabled = !allowDogs;
    if (!allowDogs) { var none = $('r-dogs0'); if (none) none.checked = true; }
    dogNote.textContent = !s ? 'Dogs come to the Sunday sessions.' : allowDogs
      ? 'Dogs are free. ' + B.dogSpotsLeft(s) + ' of ' + s.dogCapacity + ' dog spots open.'
      : 'This is a people-only session. Dogs are welcome at the Sunday sessions.';
    var n = dogCount();
    weightsBox.hidden = n === 0;
    $('r-dog2-wrap').hidden = n < 2;
    $('r-dog1').required = n === 2;
    $('r-dog2').required = n === 2;
    $('r-dog1-label').textContent = n === 1 ? 'Your dog’s weight in lb (optional, any size is welcome)' : 'Dog 1 weight (lb)';
    if (s) peopleIn.max = Math.max(1, B.spotsLeft(s));
    var people = Math.max(1, Math.floor(+peopleIn.value) || 1);
    totalOut.textContent = s
      ? people + (people === 1 ? ' person' : ' people') + ' × $' + s.price + ' = $' + B.total(s, people) + ', paid in person' + (allowDogs ? '. Dogs are free.' : '.')
      : 'Pick a session to see the price. You pay in person; nothing is charged online.';
  }

  function pick(id, focusForm) {
    var s = byId(id);
    if (!s) return;
    picked = s;
    slotSel.value = s.id;
    var p = B.dateParts(s.date);
    view = { y: p.y, m: p.m };
    renderMonth();
    renderSlots(s.date);
    syncForm();
    clearErrors();
    if (focusForm) {
      form.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
      setTimeout(function () { $('r-name').focus({ preventScroll: true }); }, 350);
    }
  }

  cal.addEventListener('click', function (e) {
    var mv = e.target.closest('[data-move]');
    if (mv) {
      var months = monthsWithSessions(), cur = months.indexOf(view.y * 12 + view.m), nx = months[cur + +mv.getAttribute('data-move')];
      if (nx) { view = { y: Math.floor((nx - 1) / 12), m: ((nx - 1) % 12) + 1 }; renderMonth(); var b = cal.querySelector('[data-move="' + mv.getAttribute('data-move') + '"]'); if (b && !b.disabled) b.focus(); }
      return;
    }
    var day = e.target.closest('[data-day]');
    if (day) {
      var iso = day.getAttribute('data-day');
      var list = data.sessions.filter(function (s) { return s.date === iso && B.isOpen(s); });
      if (list.length === 1) pick(list[0].id, false); else renderSlots(iso);
      var again = cal.querySelector('[data-day="' + iso + '"]');
      if (again) again.focus();
      return;
    }
    var pb = e.target.closest('[data-pick]');
    if (pb) pick(pb.getAttribute('data-pick'), true);
  });

  slotSel.addEventListener('change', function () {
    if (slotSel.value) pick(slotSel.value, false);
    else { picked = null; syncForm(); }
  });
  form.addEventListener('change', function (e) { if (e.target.name === 'dogs') syncForm(); });
  peopleIn.addEventListener('input', syncForm);

  function clearErrors() {
    form.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
    form.querySelectorAll('.field-error').forEach(function (el) { el.textContent = ''; });
  }
  function showErrors(errs) {
    clearErrors();
    var firstEl = null;
    errs.forEach(function (er) {
      var out = $('err-' + er.field);
      if (out) out.textContent = er.message;
      var el = er.field === 'dogs' ? (dogCount() === 2 ? $('r-dog1') : form.querySelector('input[name=dogs]:checked'))
        : er.field === 'slot' ? slotSel : $('r-' + er.field);
      if (el) { el.setAttribute('aria-invalid', 'true'); firstEl = firstEl || el; }
    });
    statusEl.textContent = errs.length === 1 ? 'Please check one thing above.' : 'Please check ' + errs.length + ' things above.';
    if (firstEl) firstEl.focus();
  }

  function readForm() {
    return {
      name: $('r-name').value.trim(), email: $('r-email').value.trim(), phone: $('r-phone').value.trim(),
      people: peopleIn.value, dogs: dogCount(), dogWeights: [$('r-dog1').value.trim(), $('r-dog2').value.trim()],
      notes: $('r-notes').value
    };
  }

  function fallback(s, r, why) {
    var text = B.summary(s, r);
    var email = (data.email || '').trim();
    var html = why + ' ';
    if (email) {
      var href = 'mailto:' + email + '?subject=' + encodeURIComponent('RSVP: ' + B.label(s)) + '&body=' + encodeURIComponent(text);
      html += 'Your email app is opening with the RSVP ready to send. <a href="' + esc(href) + '">Open it again</a> or ';
      window.location.href = href;
    }
    html += '<a href="' + esc(B.smsLink(data.phone, text)) + '">' + (email ? 'text it' : 'Tap here to text your RSVP') + ' to ' + esc(data.phone) + '</a>.';
    statusEl.innerHTML = html;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var r = readForm(), s = byId(slotSel.value);
    if ($('r-company').value) { statusEl.textContent = 'Thank you!'; return; }   // a bot filled the hidden field
    var errs = B.check(s, r);
    if (errs.length) { showErrors(errs); return; }
    clearErrors();
    var dest = B.endpoint(data.form);
    var done = function () {
      statusEl.textContent = 'Thank you, ' + r.name.split(' ')[0] + '! Your RSVP for ' + B.label(s) + ' is sent. ' +
        r.people + (+r.people === 1 ? ' person' : ' people') + ', $' + B.total(s, r.people) + ' to pay in person. See you there.';
      form.reset(); picked = null; slotSel.value = ''; syncForm();
    };
    if (!dest) { fallback(s, r, 'Almost done!'); return; }
    var payload = {
      subject: 'RSVP: ' + B.label(s), from_name: 'Sound Vibration Sanctuary website',
      session: B.label(s), date: s.date, time: B.time12(s.start), name: r.name, email: r.email, phone: r.phone,
      people: r.people, total: '$' + B.total(s, r.people) + ' (paid in person)',
      dogs: s.dogs ? String(r.dogs) : 'n/a', dog_weights_lb: r.dogs ? r.dogWeights.slice(0, r.dogs).join(', ') : '',
      notes: r.notes.trim(), message: B.summary(s, r)
    };
    if (dest.key) payload.access_key = dest.key;
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true;
    statusEl.textContent = 'Sending your RSVP…';
    fetch(dest.url, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) })
      .then(function (res) { return res.json().catch(function () { return {}; }).then(function (j) { if (!res.ok || j.success === false) throw new Error('not sent'); }); })
      .then(done, function () { fallback(s, r, 'Sorry, the RSVP didn’t go through online.'); })
      .then(function () { btn.disabled = false; });
  });

  function start(json) {
    data = json;
    data.phone = data.phone || '480-265-6136';
    var next = upcoming()[0] || data.sessions[data.sessions.length - 1];
    if (!next) { cal.querySelector('.cal-loading').textContent = 'No sessions are scheduled right now. Text ' + data.phone + ' to ask about the next ones.'; return; }
    var p = B.dateParts(next.date);
    view = { y: p.y, m: p.m };
    cal.innerHTML = '<div id="cal-month-box" class="cal-month"></div><div id="cal-slots" class="cal-slots" aria-live="polite"></div>' +
      '<p class="cal-legend"><span class="lg lg-open"></span>Spots open <span class="lg lg-dogs"></span>Dogs welcome <span class="lg lg-full"></span>Full or past</p>';
    fillSelect();
    renderMonth();
    renderSlots(null);
    syncForm();
    var want = (location.hash.match(/^#rsvp-(.+)$/) || [])[1];
    if (want && byId(want)) pick(want, false);
  }

  var getJSON = function (url) {
    return fetch(url, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  };
  Promise.all([getJSON('data/schedule.json'), getJSON('data/config.json').catch(function () { return {}; })])
    .then(function (both) {
      var where = B.settings(both[0], both[1]);
      both[0].email = where.email;
      both[0].form = where.form;
      start(both[0]);
    })
    .catch(function () {
      var l = cal.querySelector('.cal-loading');
      if (l) l.textContent = 'The calendar didn’t load. Please text 480-265-6136 to RSVP.';
    });
  syncForm();
})(this);
