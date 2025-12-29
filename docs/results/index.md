# ナンバーズ4 当選番号（最新・過去）

このページでは、**ナンバーズ4の当選番号（最新および過去）**を  
制度理解や振り返りのための **参考情報** として掲載しています。

- 本ページの情報は **参考情報** です  
- 最終的な確認は **必ず公式情報** をご参照ください  

---

## 最新の当選番号（参考・静的表示）

> ※ 下記はビルド時点の最新情報です。より新しい情報は「自動更新表示（補助）」もご参照ください。

<!-- STATIC_LATEST_START -->
- **第6888回**（2025/12/29）：**2121**
<!-- STATIC_LATEST_END -->

※ 抽選結果は各回独立しており、  
過去の結果が将来の結果を示唆・保証するものではありません。

---

## 過去の当選番号（直近10回・参考・静的表示）

> ※ 下記はビルド時点の最新情報です。より新しい情報は「自動更新表示（補助）」もご参照ください。

| 回 | 抽選日 | 当選番号 |
|---|---|---|
<!-- STATIC_HISTORY_START -->
| 6888 | 2025/12/29 | 2121 |
| 6887 | 2025/12/26 | 4141 |
| 6886 | 2025/12/25 | 6333 |
| 6885 | 2025/12/24 | 3984 |
| 6884 | 2025/12/23 | 3278 |
| 6883 | 2025/12/22 | 9785 |
| 6882 | 2025/12/19 | 4944 |
| 6881 | 2025/12/18 | 5879 |
| 6880 | 2025/12/17 | 0497 |
| 6879 | 2025/12/16 | 2310 |
<!-- STATIC_HISTORY_END -->

---

## 自動更新表示（補助・JavaScript使用）

以下は、外部JSONデータを利用して  
**最新および過去の当選番号を自動取得・表示する補助機能**です。

JavaScriptが有効な環境では、  
より新しい情報が表示される場合があります。

### 最新の当選番号（自動取得）

<div id="latest" style="padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem;">
  読み込み中…（JavaScriptが無効の場合は表示されません）
</div>

### 過去の当選番号（直近50回・自動取得）

<div id="history" style="margin-top: 1rem;">
  読み込み中…
</div>

<noscript>
  <p>
    このページの自動更新表示には JavaScript を使用しています。  
    JavaScript を有効にするか、下記のデータ参照先をご確認ください。
  </p>
</noscript>

---

## データ参照先（透明性のための明示）

- JSON（最新1件）：  
  https://hazimekom.github.io/numbers4-api/api/v1/latest.json
- JSON（全履歴・軽量）：  
  https://hazimekom.github.io/numbers4-api/api/v1/numbers4_all_min.json

---

## 公式情報

- 宝くじ公式サイト（ナンバーズ4）：  
  https://www.takarakuji-official.jp/

※ 当選番号・抽選結果の正式な確認は、必ず公式情報をご利用ください。

---

## 注意事項（誤認防止）

- 本ページは **当選を保証するものではありません**
- 本ページの情報を **予測や収益と直接結び付けないでください**
- ナンバーズ4は偶然性に基づく宝くじです  
- 最終的な判断・購入行動は利用者ご自身の責任で行ってください

---

<script>
  const API_BASE = 'https://hazimekom.github.io/numbers4-api/api/v1';

  function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function renderLatest(data) {
    const digits = Array.isArray(data.digits) ? data.digits.join('') : '----';
    const drawNo = data.draw_no ?? '---';
    const date = data.date ?? '----';

    document.getElementById('latest').innerHTML =
      `<strong>第${esc(drawNo)}回</strong>（${esc(date)}）<br>` +
      `<span style="font-size: 1.5rem; letter-spacing: 0.2rem;">${esc(digits)}</span>`;
  }

  function renderHistory(list) {
    const items = Array.isArray(list) ? list.slice(-50).reverse() : [];

    if (items.length === 0) {
      document.getElementById('history').textContent = 'データを取得できませんでした。';
      return;
    }

    const rows = items.map(x => {
      const digits = Array.isArray(x.digits) ? x.digits.join('') : '----';
      return `<tr>` +
        `<td style="padding: 0.25rem 0.5rem;">${esc(x.draw_no ?? '')}</td>` +
        `<td style="padding: 0.25rem 0.5rem;">${esc(x.date ?? '')}</td>` +
        `<td style="padding: 0.25rem 0.5rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 0.15rem;">${esc(digits)}</td>` +
      `</tr>`;
    }).join('');

    document.getElementById('history').innerHTML =
      `<table>` +
        `<thead><tr>` +
          `<th style="text-align:left; padding: 0.25rem 0.5rem;">回</th>` +
          `<th style="text-align:left; padding: 0.25rem 0.5rem;">日付</th>` +
          `<th style="text-align:left; padding: 0.25rem 0.5rem;">当選番号</th>` +
        `</tr></thead>` +
        `<tbody>${rows}</tbody>` +
      `</table>`;
  }

  Promise.all([
    fetch(`${API_BASE}/latest.json`).then(r => r.json()),
    fetch(`${API_BASE}/numbers4_all_min.json`).then(r => r.json()),
  ])
  .then(([latest, all]) => {
    renderLatest(latest);
    renderHistory(all);
  })
  .catch(() => {
    document.getElementById('latest').textContent = 'データを取得できませんでした。';
    document.getElementById('history').textContent = 'データを取得できませんでした。';
  });
</script>
