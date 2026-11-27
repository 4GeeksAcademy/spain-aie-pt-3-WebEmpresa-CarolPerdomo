"use client";

import { useState, useEffect, useCallback } from "react";
import { AlertCircle, Loader, Trash2, Edit2, Plus, Check } from "lucide-react";

interface Supplier {
  id: number;
  name: string;
  country: string;
  categories: string[];
  daily_rate: number;
  status: "active" | "inactive";
  updated_at: string;
}

interface FormData {
  name: string;
  country: string;
  categories: string[];
  daily_rate: string;
  status: "active" | "inactive";
}

const VALID_CATEGORIES = [
  "Software",
  "Hardware",
  "Services",
  "papeleria",
  "cafeteria",
];

export function SupplierDirectory() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterCountry, setFilterCountry] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [updatingRates, setUpdatingRates] = useState<Set<number>>(new Set());

  const [formData, setFormData] = useState<FormData>({
    name: "",
    country: "spain",
    categories: [],
    daily_rate: "",
    status: "active",
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchSuppliers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (filterCountry) params.append("country", filterCountry);
      if (filterCategory) params.append("category", filterCategory);

      const url = params.toString()
        ? `${API_URL}/suppliers?${params}`
        : `${API_URL}/suppliers`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Failed to fetch suppliers");
      }

      const data = await response.json();
      setSuppliers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [API_URL, filterCategory, filterCountry]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void fetchSuppliers(); }, 0);
    return () => window.clearTimeout(timer);
  }, [fetchSuppliers]);

  const handleCategoryToggle = (category: string) => {
    setFormData((prev) => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter((c) => c !== category)
        : [...prev.categories, category],
    }));
  };

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError("Supplier name is required");
      return;
    }

    if (formData.categories.length === 0) {
      setError("Select at least one category");
      return;
    }

    if (!formData.daily_rate || parseFloat(formData.daily_rate) <= 0) {
      setError("Daily rate must be a positive number");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const payload = {
        name: formData.name,
        country: formData.country,
        categories: formData.categories,
        daily_rate: parseFloat(formData.daily_rate),
        status: formData.status,
      };

      const response = await fetch(`${API_URL}/suppliers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create supplier");
      }

      await fetchSuppliers();
      resetForm();
      setShowForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSupplier = async (id: number) => {
    if (!confirm("Are you sure you want to delete this supplier?")) return;

    try {
      const response = await fetch(`${API_URL}/suppliers/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete supplier");
      }

      setSuppliers((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  const handleUpdateRate = async (
    id: number,
    newRate: string
  ) => {
    if (!newRate || parseFloat(newRate) <= 0) {
      setError("Daily rate must be a positive number");
      return;
    }

    try {
      setUpdatingRates((prev) => new Set([...prev, id]));

      const response = await fetch(`${API_URL}/suppliers/${id}/rate`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ daily_rate: parseFloat(newRate) }),
      });

      if (!response.ok) {
        throw new Error("Failed to update rate");
      }

      await fetchSuppliers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setUpdatingRates((prev) => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
    }
  };

  const handleUpdateStatus = async (
    id: number,
    newStatus: "active" | "inactive"
  ) => {
    try {
      const response = await fetch(`${API_URL}/suppliers/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error("Failed to update status");
      }

      await fetchSuppliers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      country: "spain",
      categories: [],
      daily_rate: "",
      status: "active",
    });
    setEditingId(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Supplier Directory</h1>
          <p className="mt-2 text-gray-600">
            Manage and track all company suppliers
          </p>
        </div>
        <button
          onClick={() => {
            setShowForm(!showForm);
            if (showForm) resetForm();
          }}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={20} />
          New Supplier
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="flex-shrink-0 text-red-600" size={20} />
          <div className="flex-1">
            <p className="font-medium text-red-900">{error}</p>
          </div>
        </div>
      )}

      {/* Registration Form */}
      {showForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">
            {editingId ? "Edit Supplier" : "Register New Supplier"}
          </h2>

          <form onSubmit={handleSubmitForm} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Supplier Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="Enter supplier name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <select
                value={formData.country}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, country: e.target.value }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="spain">Spain</option>
              </select>
            </div>

            {/* Categories */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product Categories * (select at least one)
              </label>
              <div className="grid grid-cols-2 gap-2">
                {VALID_CATEGORIES.map((cat) => (
                  <label key={cat} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.categories.includes(cat)}
                      onChange={() => handleCategoryToggle(cat)}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{cat}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Daily Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Daily Rate (€) *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.daily_rate}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    daily_rate: e.target.value,
                  }))
                }
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    status: e.target.value as "active" | "inactive",
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>

            {/* Form Buttons */}
            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
              >
                {loading ? "Saving..." : "Save Supplier"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
                className="flex-1 px-4 py-2 bg-gray-300 text-gray-900 rounded-lg hover:bg-gray-400 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4 bg-white p-4 rounded-lg border border-gray-200">
        <select
          value={filterCountry}
          onChange={(e) => setFilterCountry(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Countries</option>
          <option value="spain">Spain</option>
        </select>

        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Categories</option>
          {VALID_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin text-blue-600" size={32} />
        </div>
      )}

      {/* Suppliers Table */}
      {!loading && suppliers.length > 0 && (
        <div className="overflow-x-auto bg-white rounded-lg border border-gray-200">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Country
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Categories
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Daily Rate
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map((supplier) => (
                <SupplierRow
                  key={supplier.id}
                  supplier={supplier}
                  onDelete={handleDeleteSupplier}
                  onUpdateRate={handleUpdateRate}
                  onUpdateStatus={handleUpdateStatus}
                  isUpdatingRate={updatingRates.has(supplier.id)}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!loading && suppliers.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <p className="text-gray-500">No suppliers found</p>
        </div>
      )}
    </div>
  );
}

interface SupplierRowProps {
  supplier: Supplier;
  onDelete: (id: number) => void;
  onUpdateRate: (id: number, newRate: string) => void;
  onUpdateStatus: (id: number, status: "active" | "inactive") => void;
  isUpdatingRate: boolean;
}

function SupplierRow({
  supplier,
  onDelete,
  onUpdateRate,
  onUpdateStatus,
  isUpdatingRate,
}: SupplierRowProps) {
  const [editingRate, setEditingRate] = useState(false);
  const [newRate, setNewRate] = useState(supplier.daily_rate.toString());

  const handleRateSave = () => {
    onUpdateRate(supplier.id, newRate);
    setEditingRate(false);
    setNewRate(supplier.daily_rate.toString());
  };

  return (
    <tr className="border-b hover:bg-gray-50 transition">
      <td className="px-6 py-4 text-sm font-medium text-gray-900">
        {supplier.name}
      </td>
      <td className="px-6 py-4 text-sm text-gray-600">
        {supplier.country === "spain" ? "🇪🇸 Spain" : supplier.country}
      </td>
      <td className="px-6 py-4 text-sm">
        <div className="flex flex-wrap gap-1">
          {supplier.categories.map((cat) => (
            <span
              key={cat}
              className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
            >
              {cat}
            </span>
          ))}
        </div>
      </td>
      <td className="px-6 py-4 text-sm">
        {editingRate ? (
          <div className="flex gap-2">
            <input
              type="number"
              step="0.01"
              value={newRate}
              onChange={(e) => setNewRate(e.target.value)}
              className="w-24 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isUpdatingRate}
            />
            <button
              onClick={handleRateSave}
              disabled={isUpdatingRate}
              className="p-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 transition"
            >
              <Check size={16} />
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <span>€{supplier.daily_rate.toFixed(2)}</span>
            <button
              onClick={() => setEditingRate(true)}
              className="p-1 text-blue-600 hover:bg-blue-50 rounded transition"
            >
              <Edit2 size={16} />
            </button>
          </div>
        )}
      </td>
      <td className="px-6 py-4 text-sm">
        <select
          value={supplier.status}
          onChange={(e) =>
            onUpdateStatus(supplier.id, e.target.value as "active" | "inactive")
          }
          className={`px-3 py-1 rounded text-white font-medium cursor-pointer ${
            supplier.status === "active"
              ? "bg-green-600 hover:bg-green-700"
              : "bg-red-600 hover:bg-red-700"
          }`}
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </td>
      <td className="px-6 py-4 text-sm">
        <button
          onClick={() => onDelete(supplier.id)}
          className="p-2 text-red-600 hover:bg-red-50 rounded transition"
        >
          <Trash2 size={18} />
        </button>
      </td>
    </tr>
  );
}
