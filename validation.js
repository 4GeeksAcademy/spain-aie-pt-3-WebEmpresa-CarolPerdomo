(function () {
  const form = document.getElementById("nexova-application-form");
  const statusBox = document.getElementById("form-status");

  if (!form || !statusBox) {
    return;
  }

  const fields = {
    company_name: {
      required: true,
      validate(value) {
        if (value.trim().length < 2) {
          return "Ingresa el nombre legal de la empresa (minimo 2 caracteres).";
        }
        return "";
      }
    },
    contact_name: {
      required: true,
      validate(value) {
        if (value.trim().split(" ").length < 2) {
          return "Ingresa nombre y apellido del contacto principal.";
        }
        return "";
      }
    },
    contact_role: {
      required: true,
      validate(value) {
        if (value.trim().length < 3) {
          return "Indica el cargo del contacto (minimo 3 caracteres).";
        }
        return "";
      }
    },
    employee_count: {
      required: true,
      validate(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "La cantidad de empleados debe ser un numero valido.";
        }
        if (n < 20) {
          return "Nexova trabaja con empresas medianas: indica al menos 20 empleados.";
        }
        return "";
      }
    },
    sector: {
      required: true,
      validate(value) {
        const allowed = ["tecnologia", "retail", "servicios_financieros"];
        if (!allowed.includes(value)) {
          return "Selecciona un sector: tecnologia, retail o servicios financieros.";
        }
        return "";
      }
    },
    operation_country: {
      required: true,
      validate(value) {
        if (!value) {
          return "Selecciona el pais principal de operacion.";
        }
        return "";
      }
    },
    main_challenge: {
      required: true,
      validate(value) {
        if (!value) {
          return "Selecciona el reto principal para orientar el diagnostico.";
        }
        return "";
      }
    },
    target_start_date: {
      required: true,
      validate(value) {
        if (!value) {
          return "Indica una fecha objetivo de inicio.";
        }
        const selectedDate = new Date(value);
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        if (selectedDate < now) {
          return "La fecha objetivo no puede estar en el pasado.";
        }
        return "";
      }
    },
    support_sla_target_hours: {
      required: false,
      validate(value) {
        if (!value) {
          return "";
        }
        const n = Number(value);
        if (!Number.isFinite(n) || n < 1 || n > 168) {
          return "El SLA objetivo debe estar entre 1 y 168 horas.";
        }
        if (n > 24) {
          return "Para este servicio, recomendamos un SLA maximo de 24 horas.";
        }
        return "";
      }
    },
    monthly_budget_usd: {
      required: true,
      validate(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) {
          return "El presupuesto mensual debe ser un numero en USD.";
        }
        if (n < 1000) {
          return "Ingresa un presupuesto mensual realista (minimo 1000 USD).";
        }
        return "";
      }
    },
    email: {
      required: true,
      validate(value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
        if (!emailRegex.test(value.trim())) {
          return "Ingresa un email corporativo valido.";
        }
        return "";
      }
    },
    phone: {
      required: true,
      validate(value) {
        const phoneRegex = /^[+]?[0-9\s()-]{8,20}$/;
        if (!phoneRegex.test(value.trim())) {
          return "Ingresa un telefono valido con codigo de pais si aplica.";
        }
        return "";
      }
    },
    project_context: {
      required: true,
      validate(value) {
        if (value.trim().length < 30) {
          return "Describe el contexto con al menos 30 caracteres para evaluar tu caso.";
        }
        return "";
      }
    },
    terms: {
      required: true,
      validate(_, inputEl) {
        if (!inputEl.checked) {
          return "Debes aceptar el uso de datos para enviar la aplicacion.";
        }
        return "";
      }
    }
  };

  function getErrorEl(name) {
    return document.getElementById(`error-${name}`);
  }

  function updateFieldUI(inputEl, errorMessage) {
    const errorEl = getErrorEl(inputEl.name);
    if (!errorEl) {
      return;
    }

    errorEl.textContent = errorMessage;
    const baseClasses = "w-full rounded-md border bg-slate-950 px-3 py-2 text-sm focus:outline-none focus:ring-2";
    if (inputEl.tagName === "SELECT" || inputEl.tagName === "TEXTAREA" || inputEl.type !== "checkbox") {
      if (errorMessage) {
        inputEl.className = `${baseClasses} border-rose-400 focus:border-rose-300 focus:ring-rose-300/30`;
      } else {
        inputEl.className = `${baseClasses} border-emerald-400 focus:border-emerald-300 focus:ring-emerald-300/30`;
      }
    }

    inputEl.setAttribute("aria-invalid", errorMessage ? "true" : "false");
  }

  function validateServiceLines() {
    const selected = form.querySelectorAll('input[name="service_lines"]:checked');
    const errorEl = getErrorEl("service_lines");
    if (!errorEl) {
      return "";
    }
    if (selected.length === 0) {
      const message = "Selecciona al menos una linea de negocio de interes.";
      errorEl.textContent = message;
      return message;
    }
    errorEl.textContent = "";
    return "";
  }

  function validateFieldByName(name) {
    const config = fields[name];
    const inputEl = form.elements[name];
    if (!config || !inputEl) {
      return "";
    }

    const value = inputEl.type === "checkbox" ? (inputEl.checked ? "true" : "") : inputEl.value;
    let message = "";

    if (config.required && !value) {
      message = "Este campo es obligatorio.";
    } else {
      message = config.validate(value, inputEl);
    }

    updateFieldUI(inputEl, message);
    return message;
  }

  function validateAll() {
    let hasErrors = false;
    Object.keys(fields).forEach((name) => {
      const message = validateFieldByName(name);
      if (message) {
        hasErrors = true;
      }
    });

    const serviceLinesMessage = validateServiceLines();
    if (serviceLinesMessage) {
      hasErrors = true;
    }

    return !hasErrors;
  }

  Object.keys(fields).forEach((name) => {
    const inputEl = form.elements[name];
    if (!inputEl) {
      return;
    }
    inputEl.addEventListener("blur", () => validateFieldByName(name));
    inputEl.addEventListener("input", () => validateFieldByName(name));
    inputEl.addEventListener("change", () => validateFieldByName(name));
  });

  const serviceLines = form.querySelectorAll('input[name="service_lines"]');
  serviceLines.forEach((checkbox) => {
    checkbox.addEventListener("change", validateServiceLines);
  });

  form.addEventListener("reset", () => {
    Object.keys(fields).forEach((name) => {
      const inputEl = form.elements[name];
      const errorEl = getErrorEl(name);
      if (errorEl) {
        errorEl.textContent = "";
      }
      if (inputEl) {
        inputEl.removeAttribute("aria-invalid");
        if (inputEl.tagName !== "BUTTON" && inputEl.type !== "checkbox") {
          inputEl.className = "w-full rounded-md border border-slate-600 bg-slate-950 px-3 py-2 text-sm focus:border-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-300/30";
        }
      }
    });

    const serviceError = getErrorEl("service_lines");
    if (serviceError) {
      serviceError.textContent = "";
    }

    statusBox.className = "mt-4 hidden rounded-md border px-4 py-3 text-sm";
    statusBox.textContent = "";
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    statusBox.className = "mt-4 rounded-md border border-rose-400 bg-rose-950/40 px-4 py-3 text-sm text-rose-200";
    statusBox.textContent = "Revisa los campos marcados antes de enviar la aplicacion.";

    const isValid = validateAll();
    if (!isValid) {
      return;
    }

    statusBox.className = "mt-4 rounded-md border border-emerald-400 bg-emerald-950/40 px-4 py-3 text-sm text-emerald-200";
    statusBox.textContent = "Aplicacion validada correctamente. Hemos simulado el envio y el equipo de Nexova te contactara en 48 horas habiles.";
  });
})();