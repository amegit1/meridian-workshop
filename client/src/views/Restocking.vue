<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <!-- Budget input -->
    <div class="budget-bar">
      <label class="budget-label">{{ t('restocking.budgetCeiling') }}</label>
      <div class="budget-input-wrap">
        <span class="budget-symbol">$</span>
        <input
          v-model.number="budget"
          type="number"
          min="0"
          step="1000"
          :placeholder="t('restocking.budgetPlaceholder')"
          class="budget-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Summary cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.totalItems') }}</div>
          <div class="stat-value">{{ items.length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">${{ formatNumber(totalCost) }}</div>
        </div>
        <div class="stat-card" v-if="budget > 0">
          <div class="stat-label">{{ t('restocking.budgetUsed') }}</div>
          <div class="stat-value" :class="{ danger: budgetUsed > budget }">${{ formatNumber(budgetUsed) }}</div>
        </div>
        <div class="stat-card" v-if="budget > 0">
          <div class="stat-label">{{ t('restocking.budgetRemaining') }}</div>
          <div class="stat-value" :class="budgetRemaining >= 0 ? 'success' : 'danger'">${{ formatNumber(Math.abs(budgetRemaining)) }}</div>
        </div>
      </div>

      <!-- Recommendations table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.title') }}</h3>
          <span class="item-count">{{ filteredItems.length }} {{ t('common.items') }}</span>
        </div>

        <div v-if="items.length === 0" class="empty-state">
          {{ t('restocking.noItems') }}
        </div>

        <div v-else class="table-container">
          <table class="restocking-table">
            <thead>
              <tr>
                <th v-if="budget > 0">{{ t('restocking.table.recommended') }}</th>
                <th>{{ t('restocking.table.urgency') }}</th>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.name') }}</th>
                <th>{{ t('restocking.table.warehouse') }}</th>
                <th>{{ t('restocking.table.onHand') }}</th>
                <th>{{ t('restocking.table.reorderPoint') }}</th>
                <th>{{ t('restocking.table.daysRemaining') }}</th>
                <th>{{ t('restocking.table.suggestedQty') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.totalCost') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in filteredItems"
                :key="item.id"
                :class="{ 'row-recommended': isRecommended(item), 'row-over-budget': budget > 0 && !isRecommended(item) }"
              >
                <td v-if="budget > 0">
                  <span v-if="isRecommended(item)" class="check">✓</span>
                  <span v-else class="cross">—</span>
                </td>
                <td>
                  <span :class="['badge', item.urgency]">{{ t('restocking.urgency.' + item.urgency) }}</span>
                </td>
                <td><code class="sku">{{ item.sku }}</code></td>
                <td>{{ item.name }}</td>
                <td>{{ item.warehouse }}</td>
                <td>{{ item.quantity_on_hand }}</td>
                <td>{{ item.reorder_point }}</td>
                <td>
                  <span :class="daysClass(item.days_remaining)">
                    {{ item.days_remaining === 999 ? '—' : item.days_remaining + 'd' }}
                  </span>
                </td>
                <td>{{ item.suggested_qty }}</td>
                <td>${{ formatNumber(item.unit_cost) }}</td>
                <td><strong>${{ formatNumber(item.total_cost) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t } = useI18n()
    const { getCurrentFilters, selectedLocation, selectedCategory } = useFilters()

    const loading = ref(true)
    const error = ref(null)
    const items = ref([])
    const budget = ref(0)

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        items.value = await api.getRestockingRecommendations(getCurrentFilters())
      } catch (err) {
        error.value = 'Failed to load restocking data: ' + err.message
      } finally {
        loading.value = false
      }
    }

    watch([selectedLocation, selectedCategory], loadData)
    onMounted(loadData)

    const filteredItems = computed(() => items.value)

    // Greedy selection: pick items in urgency order until budget exhausted
    const recommendedIds = computed(() => {
      if (!budget.value || budget.value <= 0) return new Set()
      let remaining = budget.value
      const ids = new Set()
      for (const item of items.value) {
        if (item.total_cost <= remaining) {
          ids.add(item.id)
          remaining -= item.total_cost
        }
      }
      return ids
    })

    const isRecommended = (item) => recommendedIds.value.has(item.id)

    const totalCost = computed(() => items.value.reduce((sum, i) => sum + i.total_cost, 0))

    const budgetUsed = computed(() =>
      items.value
        .filter(i => recommendedIds.value.has(i.id))
        .reduce((sum, i) => sum + i.total_cost, 0)
    )

    const budgetRemaining = computed(() => budget.value - budgetUsed.value)

    const formatNumber = (num) => {
      if (num == null || isNaN(num)) return '0.00'
      return Number(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const daysClass = (days) => {
      if (days < 7) return 'days-critical'
      if (days < 14) return 'days-warning'
      return 'days-ok'
    }

    return {
      t,
      loading,
      error,
      items,
      budget,
      filteredItems,
      isRecommended,
      totalCost,
      budgetUsed,
      budgetRemaining,
      formatNumber,
      daysClass,
      Math
    }
  }
}
</script>

<style scoped>
.restocking { padding: 0; }

.budget-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.budget-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.375rem 0.75rem;
}

.budget-symbol {
  color: #64748b;
  font-weight: 600;
}

.budget-input {
  border: none;
  background: transparent;
  font-size: 0.938rem;
  color: #0f172a;
  width: 180px;
  outline: none;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.25rem;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #3b82f6;
}

.stat-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.stat-value.danger { color: #dc2626; }
.stat-value.success { color: #16a34a; }

.card {
  background: white;
  border-radius: 10px;
  padding: 1.25rem;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.item-count {
  font-size: 0.813rem;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.table-container { overflow-x: auto; }

.restocking-table { width: 100%; border-collapse: collapse; }
.restocking-table th {
  background: #f8fafc;
  padding: 0.625rem 0.875rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.restocking-table td {
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}

.row-recommended { background: #f0fdf4; }
.row-over-budget { opacity: 0.5; }

.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.badge.critical { background: #fee2e2; color: #991b1b; }
.badge.warning { background: #fef3c7; color: #92400e; }
.badge.low { background: #dbeafe; color: #1e40af; }

.sku {
  font-family: 'Cascadia Code', 'Consolas', monospace;
  font-size: 0.813rem;
  background: #f1f5f9;
  padding: 1px 6px;
  border-radius: 4px;
  color: #0f172a;
}

.days-critical { color: #dc2626; font-weight: 700; }
.days-warning { color: #d97706; font-weight: 600; }
.days-ok { color: #64748b; }

.check { color: #16a34a; font-weight: 700; font-size: 1rem; }
.cross { color: #94a3b8; }

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  font-size: 0.938rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.error {
  background: #fee2e2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}
</style>
