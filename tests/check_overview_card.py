"""Browser checks with fictional balances; run directly using the project venv."""

# ruff: noqa: E501
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 700})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(
        """<style>body{margin:12px;background:#151b24;--primary-text-color:#e9edf4;--secondary-text-color:#9ca8b8;--card-background-color:#202937;--divider-color:#3c4858;--primary-color:#63b6a4;--error-color:#f28b82;}</style>"""
    )
    page.add_script_tag(path=str(root / "custom_components/findash/frontend/findash-cards.js"))
    page.evaluate("""() => {
      window.ha={language:'en',states:{}};
      ['debit','credit','cushion','free'].forEach((key,i)=>ha.states['sensor.demo_'+key]={state:String([3000,500,12000,-200][i]),attributes:{findash_metric:key,findash_instance:'demo',unit_of_measurement:'USD'}});
      window.card=document.createElement('findash-overview-card');
      card.hass=ha;card.setConfig({type:'custom:findash-overview-card',language:'ru'});
      card.addEventListener('hass-more-info',e=>window.tapped=e.detail.entityId);
      document.body.append(card);
    }""")
    assert page.get_by_text("Свободно", exact=True).is_visible()
    assert page.locator("button.negative").count() == 1
    assert page.locator("button").count() == 4
    page.locator("button.free").click()
    assert page.evaluate("tapped === 'sensor.demo_free'")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path="/tmp/findash-overview-mobile.png")
    page.evaluate(
        "card.hass={...ha,states:{...ha.states,'sensor.demo_debit':{...ha.states['sensor.demo_debit'],state:'unavailable'}}}"
    )
    assert page.get_by_text("Недоступно", exact=True).is_visible()
    page.evaluate(
        "card.hass={...ha,states:{...ha.states,'sensor.duplicate':ha.states['sensor.demo_credit']}}"
    )
    assert page.get_by_text("Несколько датчиков", exact=False).is_visible()
    page.evaluate("card.hass=ha;card.setConfig({free:'sensor.missing',language:'ru'})")
    assert page.get_by_text("Датчик не найден: sensor.missing", exact=True).is_visible()
    page.evaluate("card.setConfig({language:'en',columns:4});card.style.height='240px'")
    page.set_viewport_size({"width": 1000, "height": 500})
    assert page.evaluate(
        "card.shadowRoot.querySelector('ha-card').getBoundingClientRect().height === 240"
    )
    page.screenshot(path="/tmp/findash-overview-desktop.png")
    page.evaluate("""() => {
      window.editor=customElements.get('findash-overview-card').getConfigElement();
      editor.setConfig({type:'custom:findash-overview-card',grid_options:{columns:12},visibility:[{condition:'user',users:['demo']}]});
      editor.addEventListener('config-changed',e=>window.changed=e.detail.config);
      document.body.append(editor);
    }""")
    page.get_by_label("Tile columns", exact=True).select_option("2")
    assert page.evaluate(
        "changed.columns==='2' && changed.grid_options.columns===12 && changed.visibility.length===1"
    )
    page.get_by_label("Debit entity (automatic if blank)", exact=True).fill("sensor.demo_debit")
    page.get_by_label("Debit entity (automatic if blank)", exact=True).press("Tab")
    assert page.evaluate("changed.debit === 'sensor.demo_debit'")
    assert not errors, errors
    browser.close()
print(
    "Overview browser checks passed: auto-detection, balances, negative, unavailable, ambiguous, missing, more-info, resize and visual editor."
)
