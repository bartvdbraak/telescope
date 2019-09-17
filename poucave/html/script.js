window.addEventListener('load', main);

async function main () {
  const checks = await fetchChecks();

  renderChecks(checks);

  await Promise.all(checks.map(async check => {
    const section = document.querySelector(`section#${check.project}-${check.name}`);
    section.classList.add("loading");

    const result = await fetchCheck(check);
    renderResult(section, result);
  }));
}

async function fetchChecks() {
  const resp = await fetch("/checks");
  return resp.json();
}

async function fetchCheck(check) {
  try {
    const resp = await fetch(check.url)
    return resp.json();
  } catch (e) {
    console.warn(check.project, check.name, e);
    return {success: false, data: e.toString()};
  }
}

function renderChecks(checks) {
  const checksByProject = checks.reduce((acc, check) => {
    if (!(check.project in acc)) {
      acc[check.project] = [];
    }
    acc[check.project].push(check);
    return acc;
  }, {});


  const tpl = document.getElementById("check-tpl");

  const main = document.getElementById("main");
  main.innerHTML = "";

  for(const project of Object.keys(checksByProject)) {
    const title = document.createElement("h1");
    title.textContent = project;
    main.appendChild(title);

    const grid = document.createElement("div");

    for(const check of checksByProject[project]) {
      const parameters = Object.keys(check.parameters).map(k => `${k}: ${check.parameters[k]}`).join(", ");

      const section = tpl.content.cloneNode(true);
      section.querySelector("section").setAttribute("id", `${check.project}-${check.name}`);
      section.querySelector("h1").textContent = check.name;
      section.querySelector("p.description").textContent = check.description;
      section.querySelector("p.parameters").textContent = parameters;
      section.querySelector("p.documentation").innerHTML = check.documentation.replace("\n\n", "<br/><br/>");

      grid.appendChild(section);
    }

    main.appendChild(grid);
  }
}

function renderResult(section, result) {
  section.classList.remove("loading");
  section.classList.add(result.success ? "success" : "failure");
  section.querySelector(".datetime").textContent = result.datetime;
  section.querySelector("pre.result").textContent = JSON.stringify(result.data, null, 2);
}