<!-- Production Planning Calendar - Calendar-First Design -->
<template>
  <div class="production-plan-calendar">
    <!-- Main Calendar View -->
    <div v-if="!showPlanForm && !selectedPlanForEdit" class="calendar-main">
      <!-- Large Calendar (4 Months View) -->
      <div class="calendar-container">
        <div class="calendar-header">
          <button @click="changeMonth(-1)" class="btn-nav">◄ Previous</button>
          <h3 class="calendar-title">
            {{ getMonthName(calendarMonth - 1) }} - {{ getMonthName(calendarMonth + 2) }} {{ calendarYear }}
          </h3>
          <button @click="changeMonth(1)" class="btn-nav">Next ►</button>
        </div>

        <div class="multi-month-grid">
          <div v-for="offset in [-1, 0, 1, 2]" :key="offset" class="mini-calendar">
            <div class="mini-calendar-header">
              {{ getMonthData(offset).monthName }} {{ getMonthData(offset).year }}
            </div>
            
            <div class="mini-calendar-days">
              <!-- Day Headers -->
              <div class="day-header" v-for="day in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']" :key="day">
                {{ day }}
              </div>

              <!-- Empty cells -->
              <div v-for="i in getMonthData(offset).firstDay" :key="'empty-' + offset + '-' + i" class="day-cell empty"></div>

              <!-- Days -->
              <div 
                v-for="day in getMonthData(offset).days" 
                :key="day"
                class="day-cell"
                :class="{ 
                  'today': isToday(day, offset),
                  'selected': isSelectedDate(day, offset),
                  'has-plans': getPlansForDate(day, offset).length > 0
                }"
                @click="selectDate(day, offset)"
              >
                <span class="day-num">{{ day }}</span>
                
                <!-- Dot Indicators for Plans -->
                <div class="plan-dots" v-if="getPlansForDate(day, offset).length > 0">
                  <div 
                    v-for="plan in getPlansForDate(day, offset).slice(0, 4)" 
                    :key="plan.id"
                    class="plan-dot"
                    :class="'status-' + plan.status.toLowerCase()"
                    :title="plan.plan_name"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Date Panel -->
      <div class="selected-date-panel" v-if="selectedDate">
        <div class="panel-header">
          <h4>📋 Plans for {{ formatSelectedDate() }}</h4>
          <div class="panel-actions">
            <button @click="createNewPlan" class="btn-primary">➕ Create Plan</button>
          </div>
        </div>

        <div class="plans-list" v-if="getPlansForSelectedDate().length > 0">
          <div 
            v-for="plan in getPlansForSelectedDate()" 
            :key="plan.id"
            class="plan-card"
            :class="'status-' + plan.status.toLowerCase()"
          >
            <div class="plan-card-header">
              <div class="plan-title">
                <span class="plan-type-badge">{{ plan.source_type === 'ACTUAL' ? 'SO' : plan.source_type[0] }}</span>
                <strong>{{ plan.plan_name }}</strong>
                <span v-if="plan.sales_order_id" class="so-ref">→ SO-{{ plan.sales_order_id }}</span>
              </div>
              <span :class="'status-badge status-' + plan.status.toLowerCase()">
                {{ plan.status }}
              </span>
            </div>
            <div class="plan-card-body">
              <div class="plan-info">
                <span>📦 {{ plan.items?.length || 0 }} items</span>
                <span>📅 {{ formatDate(plan.created_date) }}</span>
              </div>
            </div>
            <div class="plan-card-actions">
              <button @click="viewPlanDetails(plan)" class="btn-sm">View</button>
              <button @click="editPlan(plan)" class="btn-sm">Edit</button>
              <button 
                v-if="plan.status === 'DRAFT'" 
                @click="calculatePlan(plan.id)" 
                class="btn-sm btn-success"
              >
                Calculate
              </button>
              <button 
                v-if="plan.status === 'CALCULATED'" 
                @click="processPlan(plan.id)" 
                class="btn-sm btn-warning"
              >
                Process
              </button>
              <button @click="deletePlan(plan.id)" class="btn-sm btn-danger">Delete</button>
            </div>
          </div>
        </div>
        <div v-else class="no-plans">
          <p>No plans for this date</p>
          <button @click="createNewPlan" class="btn-primary">➕ Create First Plan</button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Plan Form -->
    <div v-if="showPlanForm" class="plan-form-container">
      <div class="form-header">
        <h3>{{ editingPlan ? 'Edit Plan' : 'Create New Plan' }} - {{ formatSelectedDate() }}</h3>
        <button @click="cancelPlanForm" class="btn-secondary">← Back to Calendar</button>
      </div>

      <div class="form-content">
        <!-- Plan Type Selection -->
        <div class="form-section">
          <h4>Plan Type</h4>
          <div class="plan-type-selector">
            <label class="radio-option">
              <input type="radio" v-model="planForm.plan_type" value="PRODUCTION" />
              <span>🏭 Production Plan</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="planForm.plan_type" value="FORECAST" />
              <span>📊 Forecast Plan</span>
            </label>
          </div>
        </div>

        <!-- Plan Name -->
        <div class="form-group">
          <label>Plan Name *</label>
          <input 
            v-model="planForm.plan_name" 
            type="text" 
            placeholder="e.g., December Production Plan"
            class="form-input"
          />
        </div>

        <!-- Source Type -->
        <div class="form-group">
          <label>Source *</label>
          <select v-model="planForm.source_type" @change="onSourceTypeChange" class="form-input">
            <option value="MANUAL">Manual Entry</option>
            <option value="ACTUAL">From Sales Order</option>
          </select>
        </div>

        <!-- Sales Order Selection -->
        <div v-if="planForm.source_type === 'ACTUAL'" class="form-section">
          <h4>📋 Select Sales Order *</h4>
          <div class="form-group">
            <label>Sales Order</label>
            <select v-model="planForm.sales_order_id" @change="loadSalesOrderItems" class="form-input">
              <option value="">-- Select Sales Order --</option>
              <option v-for="so in salesOrders" :key="so.id" :value="so.id">
                {{ so.so_number }} - {{ so.customer_name }} (Delivery: {{ formatDate(so.delivery_date) }})
              </option>
            </select>
          </div>

          <!-- SO Items Table -->
          <div v-if="planForm.sales_order_id && soItems.length > 0" class="so-items-table">
            <div class="table-header">
              <h5>Sales Order Items</h5>
              <label class="checkbox-label">
                <input type="checkbox" v-model="selectAllSOItems" @change="toggleAllSOItems" />
                Select All
              </label>
            </div>
            <table class="data-table">
              <thead>
                <tr>
                  <th width="50">
                    <input type="checkbox" v-model="selectAllSOItems" @change="toggleAllSOItems" />
                  </th>
                  <th>Item Code</th>
                  <th>Item Name</th>
                  <th>Ordered Qty</th>
                  <th>Delivery Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in soItems" :key="item.id">
                  <td>
                    <input type="checkbox" v-model="item.selected" />
                  </td>
                  <td>{{ item.item_code }}</td>
                  <td>{{ item.item_name }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>{{ formatDate(item.delivery_date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Manual Items Entry -->
        <div v-if="planForm.source_type === 'MANUAL'" class="form-section">
          <h4>📦 Plan Items</h4>
          <div v-for="(item, index) in planForm.items" :key="index" class="item-row">
            <div class="item-fields">
              <div class="form-group">
                <label>Item</label>
                <select v-model="item.item_id" class="form-input">
                  <option value="">Select Item...</option>
                  <option v-for="fg in finishedGoods" :key="fg.id" :value="fg.id">
                    {{ fg.item_code }} - {{ fg.item_name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Quantity</label>
                <input v-model.number="item.quantity" type="number" min="1" class="form-input" />
              </div>
              <div class="form-group">
                <label>Delivery Date</label>
                <input v-model="item.delivery_date" type="date" class="form-input" />
              </div>
              <button @click="removeItem(index)" class="btn-sm btn-danger">✖</button>
            </div>
          </div>
          <button @click="addItem" class="btn-sm">➕ Add Item</button>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button @click="savePlan" class="btn-primary">
            {{ editingPlan ? 'Update Plan' : 'Create Plan' }}
          </button>
          <button @click="cancelPlanForm" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Plan Details View -->
    <div v-if="selectedPlanForEdit" class="plan-details-view">
      <div class="detail-header">
        <h3>{{ selectedPlanForEdit.plan_name }}</h3>
        <button @click="selectedPlanForEdit = null" class="btn-secondary">← Back</button>
      </div>

      <div class="detail-content">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Status:</span>
            <span :class="'status-badge status-' + selectedPlanForEdit.status.toLowerCase()">
              {{ selectedPlanForEdit.status }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">Type:</span>
            <span>{{ selectedPlanForEdit.plan_type || 'PRODUCTION' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Source:</span>
            <span>{{ selectedPlanForEdit.source_type }}</span>
          </div>
          <div class="info-item" v-if="selectedPlanForEdit.sales_order_id">
            <span class="label">Sales Order:</span>
            <span class="so-ref-large">SO-{{ selectedPlanForEdit.sales_order_id }}</span>
          </div>
        </div>

        <!-- Items Table -->
        <div class="detail-section">
          <h4>📦 Plan Items</h4>
          <table class="data-table">
            <thead>
              <tr>
                <th>Item Code</th>
                <th>Item Name</th>
                <th>Quantity</th>
                <th>Delivery Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in selectedPlanForEdit.items" :key="item.id">
                <td>{{ item.item_code }}</td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ formatDate(item.delivery_date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- MRP Results -->
        <div class="detail-section" v-if="selectedPlanForEdit.mrp_results && selectedPlanForEdit.mrp_results.length > 0">
          <h4>📊 MRP Results</h4>
          <table class="data-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Required Date</th>
                <th>Gross Req</th>
                <th>On Hand</th>
                <th>Open PO</th>
                <th>Net Req</th>
                <th>Action</th>
                <th>Suggested Qty</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in selectedPlanForEdit.mrp_results" :key="result.id">
                <td>
                  <div>{{ result.item_code }}</div>
                  <div class="text-sm text-gray">{{ result.item_name }}</div>
                </td>
                <td>{{ formatDate(result.required_date) }}</td>
                <td>{{ result.gross_requirement }}</td>
                <td>{{ result.on_hand_qty }}</td>
                <td>{{ result.open_po_qty }}</td>
                <td :class="result.net_requirement > 0 ? 'text-red' : 'text-green'">
                  {{ result.net_requirement }}
                </td>
                <td>
                  <span :class="'action-badge action-' + result.suggested_action.toLowerCase()">
                    {{ result.suggested_action }}
                  </span>
                </td>
                <td>{{ result.suggested_qty }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Calculation Results Modal -->
    <div v-if="showCalculationResults" class="modal-overlay" @click="showCalculationResults = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📊 Calculation Results</h3>
          <button @click="showCalculationResults = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="results-section">
            <h4>🔧 Work Orders ({{ calculationResults.workOrders.length }})</h4>
            <table class="data-table" v-if="calculationResults.workOrders.length > 0">
              <thead>
                <tr>
                  <th>WO No</th>
                  <th>Item</th>
                  <th>Quantity</th>
                  <th>Required Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(wo, idx) in calculationResults.workOrders" :key="idx">
                  <td>{{ wo.job_no || 'Temp' }}</td>
                  <td>{{ wo.item_code }}</td>
                  <td>{{ wo.quantity }}</td>
                  <td>{{ formatDate(wo.required_date) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-else class="no-data">No work orders needed</p>
          </div>

          <div class="results-section">
            <h4>🛒 Purchase Requisitions ({{ calculationResults.purchaseReqs.length }})</h4>
            <table class="data-table" v-if="calculationResults.purchaseReqs.length > 0">
              <thead>
                <tr>
                  <th>PR No</th>
                  <th>Item</th>
                  <th>Quantity</th>
                  <th>Required Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(pr, idx) in calculationResults.purchaseReqs" :key="idx">
                  <td>{{ pr.pr_no || 'Temp' }}</td>
                  <td>{{ pr.item_code }}</td>
                  <td>{{ pr.quantity }}</td>
                  <td>{{ formatDate(pr.required_date) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-else class="no-data">No purchase requisitions needed</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCalculationResults = false" class="btn-primary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductionPlanCalendar',
  data() {
    return {
      // Calendar
      calendarMonth: new Date().getMonth(),
      calendarYear: new Date().getFullYear(),
      selectedDate: null,
      monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December'],
      dayNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      
      // Data
      allPlans: [],
      finishedGoods: [],
      salesOrders: [],
      soItems: [],
      
      // UI State
      showPlanForm: false,
      selectedPlanForEdit: null,
      editingPlan: null,
      planTypeFilter: '',
      selectAllSOItems: true,
      showCalculationResults: false,
      calculationResults: {
        workOrders: [],
        purchaseReqs: []
      },
      
      // Form
      planForm: {
        plan_type: 'PRODUCTION',
        plan_name: '',
        source_type: 'MANUAL',
        sales_order_id: '',
        items: []
      }
    }
  },
  computed: {
    filteredPlans() {
      if (!this.planTypeFilter) return this.allPlans;
      return this.allPlans.filter(p => p.plan_type === this.planTypeFilter);
    }
  },
  mounted() {
    this.loadAllPlans();
    this.loadFinishedGoods();
    this.loadSalesOrders();
  },
  methods: {
    async loadAllPlans() {
      try {
        const response = await fetch('http://localhost:8000/api/planning/plans', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.allPlans = await response.json();
      } catch (error) {
        console.error('Error loading plans:', error);
      }
    },
    
    async loadFinishedGoods() {
      try {
        const response = await fetch('http://localhost:8000/api/items?item_type=FINISHED_GOOD', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.finishedGoods = await response.json();
      } catch (error) {
        console.error('Error loading items:', error);
      }
    },

    async loadSalesOrders() {
      try {
        const response = await fetch('http://localhost:8000/api/sales/orders?status=CONFIRMED', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.salesOrders = await response.json();
      } catch (error) {
        console.error('Error loading sales orders:', error);
      }
    },

    async loadSalesOrderItems() {
      if (!this.planForm.sales_order_id) return;
      
      try {
        const response = await fetch(`http://localhost:8000/api/sales/orders/${this.planForm.sales_order_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const so = await response.json();
        this.soItems = so.items.map(item => ({
          ...item,
          selected: true
        }));
        this.selectAllSOItems = true;
      } catch (error) {
        console.error('Error loading SO items:', error);
      }
    },

    // Calendar Methods
    changeMonth(delta) {
      this.calendarMonth += delta;
      if (this.calendarMonth > 11) {
        this.calendarMonth = 0;
        this.calendarYear++;
      } else if (this.calendarMonth < 0) {
        this.calendarMonth = 11;
        this.calendarYear--;
      }
    },

    getMonthName(monthIndex) {
      // Handle wrap around for display
      let m = monthIndex;
      if (m < 0) m += 12;
      if (m > 11) m -= 12;
      return this.monthNames[m];
    },

    getMonthData(offset) {
      let m = this.calendarMonth + offset;
      let y = this.calendarYear;
      
      // Adjust year/month
      while (m > 11) {
        m -= 12;
        y++;
      }
      while (m < 0) {
        m += 12;
        y--;
      }

      const daysInMonth = new Date(y, m + 1, 0).getDate();
      const firstDay = new Date(y, m, 1).getDay();

      return {
        month: m,
        year: y,
        monthName: this.monthNames[m],
        days: daysInMonth,
        firstDay: firstDay
      };
    },

    selectDate(day, offset) {
      const data = this.getMonthData(offset);
      const dateStr = `${data.year}-${String(data.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      this.selectedDate = dateStr;
    },

    isToday(day, offset) {
      const data = this.getMonthData(offset);
      const today = new Date();
      return day === today.getDate() && 
             data.month === today.getMonth() && 
             data.year === today.getFullYear();
    },

    isSelectedDate(day, offset) {
      if (!this.selectedDate) return false;
      const data = this.getMonthData(offset);
      const dateStr = `${data.year}-${String(data.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      return this.selectedDate === dateStr;
    },

    getPlansForDate(day, offset) {
      const data = this.getMonthData(offset);
      const dateStr = `${data.year}-${String(data.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      return this.filteredPlans.filter(plan => {
        if (!plan.items || plan.items.length === 0) return false;
        return plan.items.some(item => {
          const itemDate = item.delivery_date?.split('T')[0];
          return itemDate === dateStr;
        });
      });
    },

    getPlansForSelectedDate() {
      if (!this.selectedDate) return [];
      return this.filteredPlans.filter(plan => {
        if (!plan.items || plan.items.length === 0) return false;
        return plan.items.some(item => {
          const itemDate = item.delivery_date?.split('T')[0];
          return itemDate === this.selectedDate;
        });
      });
    },

    formatSelectedDate() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate + 'T00:00:00');
      return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    },

    // Plan CRUD
    createNewPlan() {
      this.showPlanForm = true;
      this.editingPlan = null;
      this.planForm = {
        plan_type: 'PRODUCTION',
        plan_name: '',
        source_type: 'MANUAL',
        sales_order_id: '',
        items: []
      };
    },

    editPlan(plan) {
      this.showPlanForm = true;
      this.editingPlan = plan;
      this.planForm = {
        plan_type: plan.plan_type || 'PRODUCTION',
        plan_name: plan.plan_name,
        source_type: plan.source_type,
        sales_order_id: plan.sales_order_id || '',
        items: plan.items || []
      };
    },

    cancelPlanForm() {
      this.showPlanForm = false;
      this.editingPlan = null;
      this.soItems = [];
    },

    async savePlan() {
      // Validation
      if (!this.planForm.plan_name) {
        alert('Please enter a plan name');
        return;
      }

      if (this.planForm.source_type === 'ACTUAL') {
        if (!this.planForm.sales_order_id) {
          alert('Please select a Sales Order');
          return;
        }
        
        const selectedItems = this.soItems.filter(item => item.selected);
        if (selectedItems.length === 0) {
          alert('Please select at least one item from the Sales Order');
          return;
        }
        
        this.planForm.items = selectedItems.map(item => ({
          item_id: item.item_id,
          quantity: item.quantity,
          delivery_date: item.delivery_date
        }));
      } else if (this.planForm.source_type === 'MANUAL') {
        if (this.planForm.items.length === 0) {
          alert('Please add at least one item');
          return;
        }
      }

      try {
        const response = await fetch('http://localhost:8000/api/planning/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(this.planForm)
        });
        
        if (response.ok) {
          alert('Plan saved successfully');
          this.cancelPlanForm();
          this.loadAllPlans();
        } else {
          const error = await response.json();
          alert('Error: ' + (error.detail || 'Failed to save plan'));
        }
      } catch (error) {
        console.error('Error saving plan:', error);
        alert('Failed to save plan');
      }
    },

    async deletePlan(planId) {
      if (!confirm('Are you sure you want to delete this plan?')) return;
      
      try {
        const response = await fetch(`http://localhost:8000/api/planning/plans/${planId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          alert('Plan deleted successfully');
          this.loadAllPlans();
        }
      } catch (error) {
        console.error('Error deleting plan:', error);
        alert('Failed to delete plan');
      }
    },

    async viewPlanDetails(plan) {
      try {
        const response = await fetch(`http://localhost:8000/api/planning/plans/${plan.id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.selectedPlanForEdit = await response.json();
      } catch (error) {
        console.error('Error loading plan details:', error);
      }
    },

    async calculatePlan(planId) {
      if (!confirm('Run Pre-Calculation?')) return;
      
      try {
        const response = await fetch(`http://localhost:8000/api/planning/${planId}/calculate`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          const result = await response.json();
          this.calculationResults = {
            workOrders: result.temp_work_orders || [],
            purchaseReqs: result.temp_purchase_reqs || []
          };
          this.showCalculationResults = true;
          this.loadAllPlans();
        }
      } catch (error) {
        console.error('Error calculating plan:', error);
        alert('Failed to calculate plan');
      }
    },

    async processPlan(planId) {
      if (!confirm('Run Post-Calculation? This will create PRs and WOs.')) return;
      
      try {
        const response = await fetch(`http://localhost:8000/api/planning/${planId}/process`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          const result = await response.json();
          this.calculationResults = {
            workOrders: result.work_orders_created || [],
            purchaseReqs: result.prs_created || []
          };
          this.showCalculationResults = true;
          this.loadAllPlans();
        }
      } catch (error) {
        console.error('Error processing plan:', error);
        alert('Failed to process plan');
      }
    },

    // Form Methods
    onSourceTypeChange() {
      this.planForm.items = [];
      this.planForm.sales_order_id = '';
      this.soItems = [];
    },

    toggleAllSOItems() {
      this.soItems.forEach(item => {
        item.selected = this.selectAllSOItems;
      });
    },

    addItem() {
      this.planForm.items.push({
        item_id: '',
        quantity: 1,
        delivery_date: this.selectedDate || new Date().toISOString().split('T')[0]
      });
    },

    removeItem(index) {
      this.planForm.items.splice(index, 1);
    },

    // Utilities
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString();
    }
  }
}
</script>

<style scoped>
.production-plan-calendar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #c0c0c0;
  overflow: hidden; /* Prevent double scrollbars */
}

.calendar-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  overflow: hidden;
  gap: 10px;
}

/* Responsive Layout for Calendar + Panel */
@media (min-width: 1024px) {
  .calendar-main {
    flex-direction: row;
  }
  
  .calendar-container {
    flex: 2;
  }
  
  .selected-date-panel {
    flex: 1;
    min-width: 300px;
    margin-top: 0 !important;
    height: 100%;
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background: #000080;
  color: white;
  flex-wrap: wrap;
  gap: 10px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  white-space: nowrap;
}

.plan-type-select {
  padding: 5px 10px;
  border: 2px inset #808080;
  background: white;
  color: black;
  width: 100%;
  max-width: 200px;
}

.calendar-container {
  background: white;
  border: 2px inset #808080;
  padding: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background: #000080;
  color: white;
}

.calendar-title {
  margin: 0;
  font-size: 16px;
  text-align: center;
}

.btn-nav {
  padding: 5px 15px;
  background: #c0c0c0;
  border: 2px outset #808080;
  cursor: pointer;
  color: black;
  white-space: nowrap;
}

.btn-nav:active {
  border-style: inset;
}

/* Multi-Month Grid Layout */
.multi-month-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  flex: 1;
  overflow-y: auto;
  padding: 5px;
}

@media (min-width: 768px) {
  .multi-month-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
  }
}

.mini-calendar {
  border: 1px solid #808080;
  display: flex;
  flex-direction: column;
  background: white;
}

.mini-calendar-header {
  background: #c0c0c0;
  padding: 5px;
  text-align: center;
  font-weight: bold;
  font-size: 14px;
  border-bottom: 1px solid #808080;
}

.mini-calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  flex: 1;
}

.day-header {
  background: #e0e0e0;
  text-align: center;
  font-size: 10px;
  font-weight: bold;
  padding: 2px;
  border-bottom: 1px solid #c0c0c0;
}

.day-cell {
  border: 1px solid #f0f0f0;
  min-height: 40px; /* Compact height */
  padding: 2px;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.day-cell.empty {
  background: #f8f8f8;
  cursor: default;
  border: none;
}

.day-cell.today {
  background: #ffffcc;
  border: 1px solid #e6e600;
}

.day-cell.selected {
  background: #0080ff;
  color: white;
}

.day-cell.has-plans {
  background: #e0ffe0;
}

.day-cell.selected.has-plans {
  background: #0080ff;
}

.day-num {
  font-size: 12px;
  font-weight: bold;
}

/* Dot Indicators */
.plan-dots {
  display: flex;
  gap: 2px;
  margin-top: 2px;
  flex-wrap: wrap;
  justify-content: center;
}

.plan-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.plan-dot.status-draft {
  background: #808080;
}

.plan-dot.status-calculated {
  background: #ffcc00;
  border: 1px solid #997a00;
}

.plan-dot.status-processed {
  background: #00cc00;
  border: 1px solid #006600;
}

.selected-date-panel {
  background: white;
  border: 2px inset #808080;
  padding: 10px;
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 40vh; /* Limit height on mobile */
}

@media (min-width: 1024px) {
  .selected-date-panel {
    max-height: none;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 2px solid #000080;
  flex-wrap: wrap;
  gap: 5px;
}

.panel-header h4 {
  margin: 0;
  color: #000080;
  font-size: 14px;
}

.plans-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  flex: 1;
  padding-right: 5px;
}

.plan-card {
  background: white;
  border: 2px outset #808080;
  padding: 8px;
}

.plan-card.status-draft {
  border-left: 4px solid #c0c0c0;
}

.plan-card.status-calculated {
  border-left: 4px solid #ffff00;
}

.plan-card.status-processed {
  border-left: 4px solid #00ff00;
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 5px;
  gap: 5px;
}

.plan-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.so-ref {
  color: #0000ff;
  font-size: 11px;
  font-weight: bold;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: bold;
  white-space: nowrap;
}

.status-draft {
  background: #c0c0c0;
  color: #000;
}

.status-calculated {
  background: #ffff00;
  color: #000;
}

.status-processed {
  background: #00ff00;
  color: #000;
}

.plan-info {
  display: flex;
  gap: 10px;
  font-size: 11px;
  color: #666;
  margin-bottom: 8px;
}

.plan-card-actions {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary, .btn-success, .btn-warning, .btn-sm, .btn-danger, .btn-close {
  padding: 6px 12px;
  border: 2px outset #808080;
  background: #c0c0c0;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
  flex: 1;
  text-align: center;
}

@media (min-width: 600px) {
  .btn-primary, .btn-secondary, .btn-success, .btn-warning, .btn-sm, .btn-danger, .btn-close {
    flex: initial;
  }
}

.btn-primary {
  background: #000080;
  color: white;
}

.btn-success {
  background: #008000;
  color: white;
}

.btn-warning {
  background: #ff8000;
  color: white;
}

.btn-danger {
  background: #ff0000;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-close {
  background: #ff0000;
  color: white;
  font-size: 18px;
  padding: 2px 10px;
  flex: initial;
}

.no-plans {
  text-align: center;
  padding: 20px;
  color: #808080;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

/* Form Styles */
.plan-form-container, .plan-details-view {
  padding: 10px;
  background: #c0c0c0;
  overflow: auto;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
}

@media (min-width: 768px) {
  .plan-form-container, .plan-details-view {
    padding: 20px;
  }
}

.form-header, .detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #000080;
  flex-wrap: wrap;
  gap: 10px;
}

.form-header h3, .detail-header h3 {
  margin: 0;
  color: #000080;
  font-size: 16px;
}

.form-content, .detail-content {
  background: white;
  padding: 15px;
  border: 2px inset #808080;
}

.form-section {
  margin-bottom: 15px;
  padding: 10px;
  background: #f0f0f0;
  border: 1px solid #808080;
}

.form-section h4 {
  margin: 0 0 10px 0;
  color: #000080;
  font-size: 14px;
}

.plan-type-selector {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 13px;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: bold;
  font-size: 12px;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 2px inset #808080;
  background: white;
  font-size: 13px;
}

.item-row {
  background: white;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #808080;
}

.item-fields {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

@media (min-width: 600px) {
  .item-fields {
    grid-template-columns: 2fr 1fr 1fr auto;
    align-items: end;
  }
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.so-items-table {
  margin-top: 15px;
  overflow-x: auto;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 12px;
  min-width: 500px; /* Force scroll on small screens */
}

.data-table th {
  background: #000080;
  color: white;
  padding: 8px;
  text-align: left;
  border: 1px solid #000;
  white-space: nowrap;
}

.data-table td {
  padding: 6px 8px;
  border: 1px solid #c0c0c0;
}

.data-table tbody tr:hover {
  background: #ffffcc;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f0f0f0;
  border: 1px solid #808080;
}

@media (min-width: 600px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.info-item .label {
  font-weight: bold;
  font-size: 12px;
  min-width: 80px;
}

.detail-section {
  margin-top: 20px;
  overflow-x: auto;
}

.detail-section h4 {
  color: #000080;
  margin-bottom: 10px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 10px;
}

.modal-content {
  background: #c0c0c0;
  border: 4px outset #808080;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 4px 4px 0 #000;
  display: flex;
  flex-direction: column;
}

.modal-header {
  background: #000080;
  color: white;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
}

.modal-body {
  padding: 15px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 10px 15px;
  border-top: 2px solid #808080;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.results-section {
  margin-bottom: 20px;
  overflow-x: auto;
}

.results-section h4 {
  color: #000080;
  margin-bottom: 10px;
  font-size: 14px;
}
</style>
