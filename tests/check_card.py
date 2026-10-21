# ruff: noqa: E501
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 850}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(
        """<style>body {margin:12px;background:#f4f5f6;--primary-text-color:#20242a;--secondary-text-color:#69717d;--primary-color:#346d99;--divider-color:#dce0e5;--secondary-background-color:#eef0f3;} ha-card{display:block;background:white;border-radius:16px;}</style>"""
    )
    page.add_script_tag(path=str(root / "custom_components/findash/frontend/findash-cards.js"))
    page.evaluate("""() => {
      const plan={income:6000,mandatory:2400,left:3600,parts:[{id:'need',amount:1400},{id:'one_off',amount:200},{id:'pocket',amount:600},{id:'prepay',amount:1000},{id:'buffer',amount:300}],rest:100};
      const now={income:3000,mandatory:1800,left:1200,parts:[{id:'need',amount:900},{id:'one_off',amount:200},{id:'pocket',amount:400},{id:'prepay',amount:0}],rest:-300,end:{income_ahead:3000,mandatory_ahead:600,result:2100}};
      window.card=document.createElement('findash-money-flow-card'); card.setConfig({entity:'sensor.test',language:'ru'});
      window.ha={language:'ru',states:{'sensor.test':{state:'-300',attributes:{flow:{plan,now},month:'2026-10',currency:'USD',generated_at:'2026-10-18T12:00:00Z'}}}};
      card.hass=ha; document.body.append(card);
    }""")
    assert page.get_by_text("Не распределено", exact=True).is_visible()
    page.screenshot(path="/tmp/findash-card-plan.png", full_page=True)
    page.get_by_role("button", name="Этот месяц", exact=True).click()
    assert page.get_by_text("Не хватает", exact=True).is_visible()
    assert page.get_by_text("На конец месяца", exact=True).is_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path="/tmp/findash-card-now.png", full_page=True)
    page.evaluate(
        "card.hass={...ha,states:{'sensor.test':{...ha.states['sensor.test'],state:'unavailable'}}}"
    )
    assert page.get_by_text("Findash недоступен", exact=True).is_visible()
    page.evaluate("card.hass={...ha,states:{}}")
    assert page.get_by_text("Сущность не найдена: sensor.test", exact=True).is_visible()
    page.evaluate("card.setConfig({language:'ru'});card.hass=ha")
    assert page.get_by_text("Не распределено", exact=True).is_visible()
    page.evaluate("card.hass={...ha,states:{}}")
    assert page.get_by_text(
        "Home Assistant ещё не передал датчик с данными Findash", exact=True
    ).is_visible()
    page.evaluate("card.hass={...ha,states:{'sensor.renamed':ha.states['sensor.test']}}")
    assert page.get_by_text("Не распределено", exact=True).is_visible()
    page.evaluate(
        "card.hass={...ha,states:{...ha.states,'sensor.second':ha.states['sensor.test']}}"
    )
    assert page.get_by_text("Найдено несколько датчиков Findash", exact=False).is_visible()
    page.evaluate("card.setConfig({entity:' sensor.test ',language:'ru'})")
    assert page.get_by_text("Не распределено", exact=True).is_visible()
    page.evaluate(
        "card.hass=ha;card.setConfig({entity:'sensor.test',language:'en',title:'<img src=x onerror=alert(1)>'})"
    )
    assert page.get_by_text("<img src=x onerror=alert(1)>", exact=True).is_visible()
    assert page.locator("img").count() == 0
    page.evaluate(
        "document.body.style.cssText+='--primary-text-color:#eee;--secondary-text-color:#aaa;--divider-color:#444;--secondary-background-color:#333';document.querySelector('style').textContent+='ha-card{background:#20242a}'"
    )
    page.screenshot(path="/tmp/findash-card-dark.png", full_page=True)
    page.evaluate("""() => {
      window.editor = customElements.get('findash-money-flow-card').getConfigElement();
      editor.setConfig({type:'custom:findash-money-flow-card',entity:'sensor.test',grid_options:{columns:6,rows:8},visibility:[{condition:'user',users:['demo']}]});
      editor.addEventListener('config-changed', event => window.editedConfig = event.detail.config);
      document.body.append(editor);
    }""")
    page.get_by_label("Title (optional)").fill("My finances")
    page.get_by_label("Title (optional)").press("Tab")
    assert page.evaluate(
        "editedConfig.title === 'My finances' && editedConfig.grid_options.columns === 6 && editedConfig.visibility[0].users[0] === 'demo'"
    )
    page.get_by_label("Default view").select_option("now")
    assert page.evaluate("editedConfig.view === 'now'")
    page.evaluate("card.style.height='350px'")
    assert page.evaluate(
        "card.shadowRoot.querySelector('ha-card').getBoundingClientRect().height === 350"
    )
    assert not errors, errors
    browser.close()
print(
    "Card checks passed: plan, actual, shortfall, forecast, missing/unavailable, mobile width, safe title, dark theme; no JS errors."
)
