<template>
  <div class="suppliers-directory">
    <!-- Encabezado -->
    <div class="header">
      <h1>📋 Directorio de Proveedores Nexova</h1>
      <p class="subtitle">Gestión centralizada de proveedores y servicios externos</p>
    </div>

    <!-- Filtros -->
    <div class="filters">
      <div class="filter-group">
        <label for="country-filter">País:</label>
        <select id="country-filter" v-model="filterCountry" @change="applyFilters">
          <option value="">Todos</option>
          <option value="Spain">Spain 🇪🇸</option>
          <option value="USA">USA 🇺🇸</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="category-filter">Categoría:</label>
        <select id="category-filter" v-model="filterCategory" @change="applyFilters">
          <option value="">Todas</option>
          <option value="job_boards">Job Boards</option>
          <option value="ats_software">ATS Software</option>
          <option value="assessment_tools">Assessment Tools</option>
          <option value="training_platforms">Training Platforms</option>
          <option value="payroll_and_hr_software">Payroll & HR</option>
          <option value="video_interview">Video Interview</option>
          <option value="background_check">Background Check</option>
          <option value="office_and_facilities">Office & Facilities</option>
          <option value="it_and_software_licenses">IT & Software</option>
        </select>
      </div>

      <button class="btn-add" @click="toggleNewSupplierForm">
        ➕ Nuevo Proveedor
      </button>
    </div>

    <!-- Formulario de Nuevo Proveedor -->
    <div v-if="showNewSupplierForm" class="form-container">
      <h2>Registrar Nuevo Proveedor</h2>
      <form @submit.prevent="submitNewSupplier">
        <div class="form-group">
          <label for="supplier-name">Nombre del Proveedor *</label>
          <input
            id="supplier-name"
            v-model="newSupplier.name"
            type="text"
            placeholder="Ej: LinkedIn Talent Solutions"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="supplier-country">País *</label>
            <select id="supplier-country" v-model="newSupplier.country" required>
              <option value="">Seleccionar</option>
              <option value="Spain">Spain</option>
              <option value="USA">USA</option>
            </select>
          </div>

          <div class="form-group">
            <label for="supplier-currency">Moneda *</label>
            <select id="supplier-currency" v-model="newSupplier.currency" required>
              <option value="">Seleccionar</option>
              <option value="EUR">EUR (€)</option>
              <option value="USD">USD ($)</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="supplier-rate">Tarifa Mensual *</label>
          <input
            id="supplier-rate"
            v-model.number="newSupplier.monthly_rate"
            type="number"
            step="0.01"
            min="0"
            placeholder="1200.00"
            required
          />
        </div>

        <div class="form-group">
          <label for="supplier-categories">Categorías *</label>
          <select
            id="supplier-categories"
            v-model="newSupplier.categories"
            multiple
            required
          >
            <option value="job_boards">Job Boards</option>
            <option value="ats_software">ATS Software</option>
            <option value="assessment_tools">Assessment Tools</option>
            <option value="training_platforms">Training Platforms</option>
            <option value="payroll_and_hr_software">Payroll & HR</option>
            <option value="video_interview">Video Interview</option>
            <option value="background_check">Background Check</option>
            <option value="office_and_facilities">Office & Facilities</option>
            <option value="it_and_software_licenses">IT & Software</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="supplier-email">Email de Contacto</label>
            <input
              id="supplier-email"
              v-model="newSupplier.contact_email"
              type="email"
              placeholder="contact@supplier.com"
            />
          </div>

          <div class="form-group">
            <label for="supplier-renewal">Fecha de Renovación</label>
            <input
              id="supplier-renewal"
              v-model="newSupplier.contract_renewal_date"
              type="date"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="supplier-notes">Notas</label>
          <textarea
            id="supplier-notes"
            v-model="newSupplier.notes"
            placeholder="Observaciones internas..."
            rows="3"
          ></textarea>
        </div>

        <div v-if="formError" class="error-message">
          ⚠️ {{ formError }}
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary">Registrar</button>
          <button
            type="button"
            class="btn-secondary"
            @click="toggleNewSupplierForm"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>

    <!-- Tabla de Proveedores -->
    <div class="table-container">
      <table v-if="filteredSuppliers.length > 0" class="suppliers-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>País</th>
            <th>Categorías</th>
            <th>Tarifa Mensual</th>
            <th>Estado</th>
            <th>Renovación</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="supplier in filteredSuppliers"
            :key="supplier.id"
            :class="{ suspended: supplier.status === 'suspended' }"
          >
            <td class="supplier-name">{{ supplier.name }}</td>
            <td class="country">
              {{ supplier.country === "Spain" ? "🇪🇸 Spain" : "🇺🇸 USA" }}
            </td>
            <td class="categories">
              <div class="category-badges">
                <span
                  v-for="cat in supplier.categories"
                  :key="cat"
                  class="badge"
                >
                  {{ formatCategory(cat) }}
                </span>
              </div>
            </td>
            <td class="rate">
              <span v-if="editingRateId !== supplier.id">
                {{ supplier.monthly_rate.toFixed(2) }} {{ supplier.currency }}
              </span>
              <input
                v-else
                v-model.number="editingRateValue"
                type="number"
                step="0.01"
                min="0"
              />
            </td>
            <td class="status">
              <span
                :class="{
                  badge: true,
                  active: supplier.status === 'active',
                  suspended: supplier.status === 'suspended',
                }"
              >
                {{ supplier.status === "active" ? "✅ Activo" : "⏸️ Suspendido" }}
              </span>
            </td>
            <td class="renewal">
              {{ supplier.contract_renewal_date || "—" }}
            </td>
            <td class="actions">
              <div class="action-buttons">
                <button
                  v-if="editingRateId === supplier.id"
                  @click="saveRate(supplier.id)"
                  class="btn-small btn-save"
                  title="Guardar tarifa"
                >
                  💾
                </button>
                <button
                  v-else
                  @click="editRate(supplier.id, supplier.monthly_rate)"
                  class="btn-small btn-edit"
                  title="Editar tarifa"
                >
                  ✏️
                </button>

                <button
                  @click="toggleStatus(supplier.id, supplier.status)"
                  :class="[
                    'btn-small',
                    supplier.status === 'active' ? 'btn-suspend' : 'btn-activate',
                  ]"
                  :title="
                    supplier.status === 'active'
                      ? 'Suspender'
                      : 'Activar'
                  "
                >
                  {{ supplier.status === "active" ? "🔒" : "🔓" }}
                </button>

                <button
                  @click="deleteSupplier(supplier.id)"
                  class="btn-small btn-delete"
                  title="Eliminar"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">
        <p>No se encontraron proveedores con los filtros seleccionados.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SuppliersDirectory",
  data() {
    return {
      suppliers: [],
      filteredSuppliers: [],
      filterCountry: "",
      filterCategory: "",
      showNewSupplierForm: false,
      newSupplier: {
        name: "",
        country: "",
        currency: "",
        monthly_rate: "",
        categories: [],
        contact_email: "",
        contract_renewal_date: "",
        notes: "",
        status: "active",
      },
      formError: "",
      editingRateId: null,
      editingRateValue: 0,
      apiUrl: "http://localhost:8000",
    };
  },
  mounted() {
    this.loadSuppliers();
  },
  methods: {
    async loadSuppliers() {
      try {
        const response = await fetch(`${this.apiUrl}/suppliers`);
        if (response.ok) {
          this.suppliers = await response.json();
          this.applyFilters();
        }
      } catch (error) {
        console.error("Error cargando proveedores:", error);
      }
    },
    applyFilters() {
      this.filteredSuppliers = this.suppliers.filter((supplier) => {
        const countryMatch =
          !this.filterCountry || supplier.country === this.filterCountry;
        const categoryMatch =
          !this.filterCategory ||
          supplier.categories.includes(this.filterCategory);
        return countryMatch && categoryMatch;
      });
    },
    toggleNewSupplierForm() {
      this.showNewSupplierForm = !this.showNewSupplierForm;
      if (!this.showNewSupplierForm) {
        this.resetForm();
      }
    },
    resetForm() {
      this.newSupplier = {
        name: "",
        country: "",
        currency: "",
        monthly_rate: "",
        categories: [],
        contact_email: "",
        contract_renewal_date: "",
        notes: "",
        status: "active",
      };
      this.formError = "";
    },
    async submitNewSupplier() {
      this.formError = "";

      if (!this.newSupplier.name || !this.newSupplier.country) {
        this.formError = "Nombre y País son requeridos";
        return;
      }

      try {
        const response = await fetch(`${this.apiUrl}/suppliers`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.newSupplier),
        });

        if (!response.ok) {
          const error = await response.json();
          this.formError = error.detail || "Error al registrar proveedor";
          return;
        }

        this.showNewSupplierForm = false;
        this.resetForm();
        this.loadSuppliers();
      } catch (error) {
        this.formError = `Error: ${error.message}`;
      }
    },
    editRate(id, currentRate) {
      this.editingRateId = id;
      this.editingRateValue = currentRate;
    },
    async saveRate(id) {
      if (this.editingRateValue <= 0) {
        alert("La tarifa debe ser mayor a 0");
        return;
      }

      try {
        const response = await fetch(`${this.apiUrl}/suppliers/${id}/rate`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ monthly_rate: this.editingRateValue }),
        });

        if (response.ok) {
          this.editingRateId = null;
          this.loadSuppliers();
        } else {
          alert("Error al actualizar tarifa");
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    },
    async toggleStatus(id, currentStatus) {
      const newStatus = currentStatus === "active" ? "suspended" : "active";

      try {
        const response = await fetch(`${this.apiUrl}/suppliers/${id}/status`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: newStatus }),
        });

        if (response.ok) {
          this.loadSuppliers();
        } else {
          alert("Error al actualizar estado");
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    },
    async deleteSupplier(id) {
      if (!confirm("¿Estás seguro de que deseas eliminar este proveedor?")) {
        return;
      }

      try {
        const response = await fetch(`${this.apiUrl}/suppliers/${id}`, {
          method: "DELETE",
        });

        if (response.ok || response.status === 204) {
          this.loadSuppliers();
        } else {
          alert("Error al eliminar proveedor");
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    },
    formatCategory(category) {
      const mapping = {
        job_boards: "Job Boards",
        ats_software: "ATS",
        assessment_tools: "Assessment",
        training_platforms: "Training",
        payroll_and_hr_software: "Payroll & HR",
        video_interview: "Video Interview",
        background_check: "Background Check",
        office_and_facilities: "Office & Facilities",
        it_and_software_licenses: "IT & Software",
      };
      return mapping[category] || category;
    },
  },
};
</script>

<style scoped>
.suppliers-directory {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 12px;
}

.header {
  margin-bottom: 2rem;
  text-align: center;
}

.header h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin: 0.5rem 0 0;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.filter-group select {
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
}

.btn-add {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-add:hover {
  background: #45a049;
}

.form-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 2px solid #4CAF50;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-container h2 {
  margin-top: 0;
  color: #333;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
}

.form-group select[multiple] {
  min-height: 120px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #c33;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-secondary {
  background: #ddd;
  color: #333;
}

.btn-secondary:hover {
  background: #ccc;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow-x: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.suppliers-table {
  width: 100%;
  border-collapse: collapse;
}

.suppliers-table thead {
  background: #f0f0f0;
  border-bottom: 2px solid #ddd;
}

.suppliers-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.suppliers-table tbody tr {
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.suppliers-table tbody tr:hover {
  background: #f9f9f9;
}

.suppliers-table tbody tr.suspended {
  opacity: 0.6;
  background: #f5f5f5;
}

.suppliers-table td {
  padding: 1rem;
  font-size: 0.95rem;
  color: #333;
}

.supplier-name {
  font-weight: 600;
}

.country {
  text-align: center;
}

.categories {
  min-width: 250px;
}

.category-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge.active {
  background: #c8e6c9;
  color: #2e7d32;
}

.badge.suspended {
  background: #ffccbc;
  color: #d84315;
}

.rate {
  font-weight: 600;
  color: #2e7d32;
  min-width: 150px;
}

.rate input {
  width: 100px;
  padding: 0.4rem 0.6rem;
  border: 1px solid #4CAF50;
  border-radius: 4px;
  font-size: 0.95rem;
}

.status {
  text-align: center;
}

.renewal {
  font-size: 0.9rem;
  color: #666;
}

.actions {
  min-width: 150px;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-small {
  padding: 0.4rem 0.6rem;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
}

.btn-small:hover {
  transform: scale(1.1);
  opacity: 0.8;
}

.btn-save {
  background: #4CAF50;
  color: white;
}

.btn-edit {
  background: #2196F3;
  color: white;
}

.btn-suspend {
  background: #ff9800;
  color: white;
}

.btn-activate {
  background: #4CAF50;
  color: white;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.empty-state {
  padding: 3rem 2rem;
  text-align: center;
  color: #666;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }

  .filter-group,
  .btn-add {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .suppliers-table {
    font-size: 0.85rem;
  }

  .suppliers-table th,
  .suppliers-table td {
    padding: 0.75rem 0.5rem;
  }

  .action-buttons {
    justify-content: space-around;
  }
}
</style>
