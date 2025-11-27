<template>
  <!-- Login Screen -->
  <LoginScreen v-if="!isLoggedIn" @login-success="handleLoginSuccess" />

  <!-- Desktop Environment -->
  <div 
    v-else
    class="h-screen w-screen overflow-hidden bg-[#c4b5a0] relative select-none font-sans"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @click="showStartMenu = false"
  >
    <!-- Desktop Icons -->
    <div
      v-for="icon in icons"
      :key="icon.id"
      draggable="true"
      @dragstart="(e) => handleIconDragStart(e, icon.id)"
      @drag="(e) => handleIconDrag(e, icon.id)"
      @dragend="handleIconDragEnd"
      @dblclick="handleIconDoubleClick(icon)"
      :style="{ left: `${icon.x}px`, top: `${icon.y}px` }"
      class="absolute cursor-pointer flex flex-col items-center w-20"
    >
      <div class="w-16 h-16 flex items-center justify-center">
        <component 
          :is="icon.icon" 
          class="w-14 h-14 text-amber-900 drop-shadow-lg" 
          :stroke-width="1.5"
        />
      </div>
      <span v-if="icon.nameKey" class="text-xs mt-1 text-stone-900 font-bold text-center drop-shadow-sm">
        {{ $t(icon.nameKey) }}
      </span>
    </div>

    <!-- Calendar Widget -->
    <div v-if="showCalendar" class="absolute top-12 right-4 bg-stone-300 border-4 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 rounded-lg shadow-2xl w-[220px] z-50">
      <div class="bg-gradient-to-r from-olive-700 to-olive-600 text-stone-100 text-center py-1 mb-2 border-b-2 border-stone-500 flex items-center justify-between px-2">
        <button 
          @click="changeMonth(-1)"
          class="text-xs font-bold hover:bg-olive-800 px-1 rounded"
        >
          ◄
        </button>
        <span class="text-xs font-bold">{{ monthNames[calendarMonth] }} {{ calendarYear }}</span>
        <button 
          @click="changeMonth(1)"
          class="text-xs font-bold hover:bg-olive-800 px-1 rounded"
        >
          ►
        </button>
      </div>
      <div class="grid grid-cols-7 gap-0 text-[10px] font-bold mb-1 px-2">
        <div v-for="day in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']" :key="day" class="text-center text-stone-700">{{ day }}</div>
      </div>
      <div class="grid grid-cols-7 gap-0 bg-stone-200 p-1 mx-2 mb-2 border border-stone-400">
        <div v-for="i in firstDay" :key="`empty-${i}`" class="text-center p-1"></div>
        <div 
          v-for="i in daysInMonth" 
          :key="i"
          class="text-center p-1 text-xs font-bold relative"
          :class="[
            isToday(i) ? 'bg-red-500 text-white' : 'text-stone-800',
            getEvent(i) ? 'cursor-pointer hover:bg-stone-300' : ''
          ]"
          :title="getEvent(i)?.title"
        >
          {{ i }}
          <div 
            v-if="getEvent(i)" 
            class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full"
            :class="getEvent(i).color"
          ></div>
        </div>
      </div>
      
      <!-- Events List -->
      <div class="px-2 pb-2 max-h-48 overflow-y-auto">
        <div class="text-[10px] font-bold mb-1 text-stone-800 bg-stone-400 px-2 py-1 border border-stone-500">
          Events this month
        </div>
        <div class="space-y-1">
          <template v-if="monthEvents.length > 0">
            <div 
              v-for="(event, idx) in monthEvents" 
              :key="idx"
              class="bg-white border border-stone-400 px-2 py-1 text-[10px] hover:bg-stone-100 cursor-pointer"
            >
              <div class="flex items-center gap-1">
                <div class="w-2 h-2 rounded-full" :class="event.color"></div>
                <span class="font-bold text-stone-700">{{ event.date }} {{ monthNamesTH[calendarMonth].substring(0, 3) }}</span>
              </div>
              <div class="text-stone-800 ml-3">{{ event.title }}</div>
            </div>
          </template>
          <div v-else class="bg-white border border-stone-400 px-2 py-1 text-[10px] text-stone-600 text-center">
            No events
          </div>
        </div>
      </div>
      
      <!-- Legend -->
      <div class="px-2 pb-2 border-t border-stone-400 pt-2 mt-2">
        <div class="text-[9px] font-bold mb-1 text-stone-700">Legend:</div>
        <div class="grid grid-cols-2 gap-1 text-[8px]">
          <div class="flex items-center gap-1"><div class="w-2 h-2 bg-blue-500 rounded-full"></div><span>รับสินค้า</span></div>
          <div class="flex items-center gap-1"><div class="w-2 h-2 bg-green-600 rounded-full"></div><span>ส่งออเดอร์</span></div>
          <div class="flex items-center gap-1"><div class="w-2 h-2 bg-amber-600 rounded-full"></div><span>การเงิน</span></div>
          <div class="flex items-center gap-1"><div class="w-2 h-2 bg-purple-600 rounded-full"></div><span>สต็อก</span></div>
        </div>
      </div>
    </div>

    <!-- Windows -->
    <div
      v-for="window in windows"
      :key="window.id"
      v-show="!window.minimized"
      :style="window.maximized 
        ? { left: '0px', top: '0px', width: '100%', height: 'calc(100% - 48px)', zIndex: window.zIndex }
        : { left: `${window.x}px`, top: `${window.y}px`, width: `${window.width}px`, height: `${window.height}px`, zIndex: window.zIndex }"
      class="absolute bg-stone-300 border-4 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 shadow-2xl flex flex-col"
      @mousedown="(e) => handleWindowMouseDown(e, window.id)"
    >
      <!-- Title Bar -->
      <div class="window-titlebar bg-gradient-to-r from-olive-700 to-olive-600 text-stone-100 px-2 py-1 flex justify-between items-center cursor-move border-b-2 border-stone-500">
        <div class="flex items-center gap-2">
          <Package class="w-4 h-4" />
          <span class="font-bold text-sm">{{ window.title }}</span>
        </div>
        <div class="flex gap-1">
          <button @click.stop="minimizeWindow(window.id)" class="w-5 h-5 bg-stone-300 hover:bg-stone-200 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 flex items-center justify-center text-stone-800 font-bold">_</button>
          <button @click.stop="toggleMaximize(window.id)" class="w-5 h-5 bg-stone-300 hover:bg-stone-200 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 flex items-center justify-center text-stone-800 font-bold">□</button>
          <button @click.stop="closeWindow(window.id)" class="w-5 h-5 bg-stone-300 hover:bg-stone-200 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 flex items-center justify-center text-stone-800 font-bold">×</button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-auto bg-stone-200 p-1 relative">
        <div v-if="window.content === 'items-table'" class="h-full flex flex-col">
          <!-- Toolbar -->
          <div class="p-2 bg-stone-300 border-b-2 border-stone-500 flex gap-2">
            <button v-if="(userRole === 'admin' || userRole === 'manager') && window.data?.allowAdd" @click="handleAddItem" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
              + Add Item
            </button>
            <button @click="exportToCSV(filteredInventory, 'inventory.csv')" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
              Export CSV
            </button>
          </div>
          
          <div class="overflow-auto border-2 border-stone-400 bg-white">
            <table class="w-full text-xs border-collapse">
              <thead>
                <tr class="bg-stone-300 border-b-2 border-stone-500">
                  <th 
                    v-for="col in [
                      { key: 'id', label: 'Item ID', align: 'left' },
                      { key: 'desc', label: 'Description', align: 'left' },
                      { key: 'category', label: 'Category', align: 'left' },
                      { key: 'qty', label: 'Quantity', align: 'right' },
                      { key: 'reorder', label: 'Reorder Level', align: 'right' },
                      { key: 'status', label: 'Status', align: 'left' }
                    ]" 
                    :key="col.key"
                    class="border-r border-stone-400 px-2 py-1 font-bold select-none cursor-pointer hover:bg-stone-200 relative"
                    :class="`text-${col.align}`"
                    @click="handleHeaderClick(col.key)"
                    @dblclick.stop="handleHeaderDoubleClick(col.key)"
                  >
                    <div class="flex items-center gap-1" :class="col.align === 'right' ? 'justify-end' : 'justify-start'">
                      <span>{{ col.label }}</span>
                      <div v-if="sortKey === col.key" class="text-stone-600">
                        <ArrowUp v-if="sortOrder === 'asc'" class="w-3 h-3" />
                        <ArrowDown v-else class="w-3 h-3" />
                      </div>
                      <Search v-if="searchFilters[col.key]" class="w-3 h-3 text-olive-600" />
                    </div>
                    
                    <!-- Search Input Popup -->
                    <div 
                      v-if="activeSearchColumn === col.key"
                      class="absolute top-full left-0 z-50 bg-stone-200 border-2 border-stone-500 p-1 shadow-lg min-w-[150px]"
                      @click.stop
                    >
                      <input 
                        v-model="searchFilters[col.key]"
                        type="text"
                        class="w-full text-xs px-1 border border-stone-400 outline-none"
                        placeholder="Search..."
                        autoFocus
                      />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(row, idx) in filteredInventory" 
                  :key="idx" 
                  :class="idx % 2 === 0 ? 'bg-white' : 'bg-stone-50'"
                  class="hover:bg-blue-100 cursor-pointer"
                  @dblclick="handleRowDoubleClick(row)"
                >
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.id }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.desc }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.category }}</td>
                  <td class="border-r border-stone-300 px-2 py-1 text-right">{{ row.qty }}</td>
                  <td class="border-r border-stone-300 px-2 py-1 text-right">{{ row.reorder }}</td>
                  <td class="px-2 py-1">{{ row.status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-1 flex gap-1">
            <div class="h-4 bg-stone-400 border-2 border-stone-500 flex-1"></div>
            <div class="w-4 h-4 bg-stone-400 border-2 border-stone-500"></div>
          </div>
        </div>

        <!-- Partners Table -->
        <div v-else-if="window.content === 'partners-table'" class="h-full flex flex-col">
          <!-- Toolbar -->
          <div class="p-2 bg-stone-300 border-b-2 border-stone-500 flex gap-2">
            <button v-if="userRole === 'admin' || userRole === 'manager'" @click="handleAddPartner" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
              + Add Partner
            </button>
            <button @click="exportToCSV(filteredPartners, 'partners.csv')" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
              Export CSV
            </button>
          </div>
          
          <div class="overflow-auto border-2 border-stone-400 bg-white">
            <table class="w-full text-xs border-collapse">
              <thead>
                <tr class="bg-stone-300 border-b-2 border-stone-500">
                  <th 
                    v-for="col in [
                      { key: 'code', label: 'Code', align: 'left' },
                      { key: 'name', label: 'Name', align: 'left' },
                      { key: 'type', label: 'Type', align: 'left' },
                      { key: 'phone', label: 'Phone', align: 'left' },
                      { key: 'email', label: 'Email', align: 'left' },
                      { key: 'status', label: 'Status', align: 'left' }
                    ]" 
                    :key="col.key"
                    class="border-r border-stone-400 px-2 py-1 font-bold select-none cursor-pointer hover:bg-stone-200 relative"
                    :class="`text-${col.align}`"
                    @click="handleHeaderClick(col.key)"
                    @dblclick.stop="handleHeaderDoubleClick(col.key)"
                  >
                    <div class="flex items-center gap-1" :class="col.align === 'right' ? 'justify-end' : 'justify-start'">
                      <span>{{ col.label }}</span>
                      <div v-if="sortKey === col.key" class="text-stone-600">
                        <ArrowUp v-if="sortOrder === 'asc'" class="w-3 h-3" />
                        <ArrowDown v-else class="w-3 h-3" />
                      </div>
                      <Search v-if="searchFilters[col.key]" class="w-3 h-3 text-olive-600" />
                    </div>
                    
                    <div 
                      v-if="activeSearchColumn === col.key"
                      class="absolute top-full left-0 z-50 bg-stone-200 border-2 border-stone-500 p-1 shadow-lg min-w-[150px]"
                      @click.stop
                    >
                      <input 
                        v-model="searchFilters[col.key]"
                        type="text"
                        class="w-full text-xs px-1 border border-stone-400 outline-none"
                        placeholder="Search..."
                        autoFocus
                      />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(row, idx) in filteredPartners" 
                  :key="idx" 
                  :class="idx % 2 === 0 ? 'bg-white' : 'bg-stone-50'"
                  class="hover:bg-blue-100 cursor-pointer"
                  @dblclick="handleRowDoubleClick(row)"
                >
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.code }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.name }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.type }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.phone }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.email }}</td>
                  <td class="px-2 py-1">{{ row.status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-1 flex gap-1">
            <div class="h-4 bg-stone-400 border-2 border-stone-500 flex-1"></div>
            <div class="w-4 h-4 bg-stone-400 border-2 border-stone-500"></div>
          </div>
        </div>
        
        <!-- Partner Master Content -->
        <div v-else-if="window.content === 'partner-master'" class="p-2 bg-stone-200 h-full overflow-auto">
          <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4 space-y-4">
            <div class="flex gap-4 items-start">
              <div class="w-24 h-24 bg-white border-2 border-stone-500 flex items-center justify-center">
                <Users class="w-12 h-12 text-stone-400" />
              </div>
              <div class="flex-1 space-y-2">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-stone-700">Partner Code</label>
                    <div class="bg-white border border-stone-500 px-2 py-1 text-sm font-bold">{{ window.data.code }}</div>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-stone-700">Type</label>
                    <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.type }}</div>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Name</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.name }}</div>
                </div>
              </div>
            </div>

            <fieldset class="border-2 border-stone-400 p-2 mt-4">
              <legend class="text-xs font-bold px-1 text-stone-700">Contact Details</legend>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-stone-700">Tax ID</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.taxId }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Status</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.status }}</div>
                </div>
                <div class="col-span-2">
                  <label class="block text-xs font-bold text-stone-700">Address</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm h-16">{{ window.data._raw.address }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Phone</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.phone }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Email</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.email }}</div>
                </div>
              </div>
            </fieldset>

            <div class="flex justify-between mt-4">
              <div class="flex gap-2" v-if="userRole === 'admin' || userRole === 'manager'">
                <button @click="handleEditPartner(window.data)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                  Edit
                </button>
                <button @click="handleDisablePartner(window.data)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm text-red-700 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                  Disable
                </button>
              </div>
              <div class="flex gap-2" v-else>
                <div></div>
              </div>

              <button @click="closeWindow(window.id)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                Close
              </button>
            </div>
          </div>
        </div>
        
        <!-- Item Master Content -->
        <div v-else-if="window.content === 'item-master'" class="p-2 bg-stone-200 h-full overflow-auto">
          <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4 space-y-4">
            <div class="flex gap-4 items-start">
              <div class="w-24 h-24 bg-white border-2 border-stone-500 flex items-center justify-center">
                <Package class="w-12 h-12 text-stone-400" />
              </div>
              <div class="flex-1 space-y-2">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-stone-700">Item Code</label>
                    <div class="bg-white border border-stone-500 px-2 py-1 text-sm font-bold">{{ window.data.id }}</div>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-stone-700">Status</label>
                    <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.status }}</div>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Description</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.desc }}</div>
                </div>
              </div>
            </div>

            <fieldset class="border-2 border-stone-400 p-2 mt-4">
              <legend class="text-xs font-bold px-1 text-stone-700">Inventory Details</legend>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-stone-700">Category</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.category }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Unit</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data._raw.unit }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Current Quantity</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm text-right font-mono">{{ window.data.qty }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Reorder Point</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm text-right font-mono">{{ window.data.reorder }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Standard Cost</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm text-right font-mono">{{ window.data._raw.standard_cost }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Selling Price</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm text-right font-mono">{{ window.data._raw.selling_price }}</div>
                </div>
              </div>
            </fieldset>

            <div class="flex justify-between mt-4">
              <div class="flex gap-2" v-if="userRole === 'admin' || userRole === 'manager'">
                <button @click="handleEditItem(window.data)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                  Edit
                </button>
                <button @click="handleDisableItem(window.data)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm text-red-700 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                  Disable
                </button>
              </div>
              <div class="flex gap-2" v-else>
                <!-- Spacer for user role -->
                <div></div>
              </div>
              
              <button @click="closeWindow(window.id)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                Close
              </button>
            </div>
          </div>
        </div>

        <!-- Locations Table -->
        <div v-else-if="window.content === 'locations-table'" class="flex flex-col h-full">
          <div class="bg-stone-300 border-b-2 border-stone-500 p-1 flex gap-2">
            <button 
              v-if="userRole === 'admin' || userRole === 'manager'"
              @click="openLocationForm('add', null, window.id)"
              class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 text-sm font-bold flex items-center gap-1"
            >
              <div class="w-3 h-3 bg-green-600 border border-stone-500"></div>
              Add Location
            </button>
          </div>
          
          <div class="flex-1 bg-white overflow-auto p-1">
            <table class="w-full text-left border-collapse text-sm">
              <thead class="bg-stone-300 sticky top-0">
                <tr>
                  <th class="border border-stone-500 px-2 py-1">Warehouse</th>
                  <th class="border border-stone-500 px-2 py-1">Code</th>
                  <th class="border border-stone-500 px-2 py-1">Zone</th>
                  <th class="border border-stone-500 px-2 py-1">Condition</th>
                  <th class="border border-stone-500 px-2 py-1">Secure</th>
                  <th class="border border-stone-500 px-2 py-1">Floor</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="loc in locationsData" 
                  :key="loc.id"
                  class="hover:bg-blue-700 hover:text-white cursor-pointer"
                  @dblclick="openLocationForm('edit', loc, window.id)"
                >
                  <td class="border border-stone-300 px-2 py-1">{{ getWarehouseName(loc.warehouse_id) }}</td>
                  <td class="border border-stone-300 px-2 py-1 font-bold">{{ loc.location_code }}</td>
                  <td class="border border-stone-300 px-2 py-1">{{ loc.zone_type }}</td>
                  <td class="border border-stone-300 px-2 py-1">{{ loc.condition_type }}</td>
                  <td class="border border-stone-300 px-2 py-1 text-center">{{ loc.is_secure_cage ? 'Yes' : 'No' }}</td>
                  <td class="border border-stone-300 px-2 py-1 text-right">{{ loc.floor_level }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Users Table -->
        <div v-else-if="window.content === 'users-table'" class="flex flex-col h-full">
          <!-- Stats Bar -->
          <div class="bg-stone-300 border-b-2 border-stone-400 px-2 py-1 text-xs flex items-center gap-4">
            <span class="font-bold">Total: {{ userStats.total_users }}</span>
            <span class="text-green-700">Active: {{ userStats.active_users }}</span>
            <span class="text-red-700">Inactive: {{ userStats.inactive_users }}</span>
            <span class="text-blue-700">Admins: {{ userStats.by_role?.admin || 0 }}</span>
            <span class="text-purple-700">Managers: {{ userStats.by_role?.manager || 0 }}</span>
            <span class="text-stone-600">Users: {{ userStats.by_role?.user || 0 }}</span>
          </div>
          
          <!-- Toolbar -->
          <div class="bg-stone-300 border-b-2 border-stone-500 p-1 flex gap-2">
            <button 
              v-if="userRole === 'admin'"
              @click="openUserForm('add', null, window.id)"
              class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 text-sm font-bold flex items-center gap-1"
            >
              <div class="w-3 h-3 bg-green-600 border border-stone-500"></div>
              Add User
            </button>
            <button 
              @click="fetchUsers"
              class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 text-sm font-bold flex items-center gap-1"
            >
              <RefreshCw class="w-3 h-3" />
              Refresh
            </button>
          </div>
          
          <div class="flex-1 bg-white overflow-auto p-1">
            <table class="w-full text-left border-collapse text-sm">
              <thead class="bg-stone-300 sticky top-0">
                <tr>
                  <th class="border border-stone-500 px-2 py-1">ID</th>
                  <th class="border border-stone-500 px-2 py-1">Username</th>
                  <th class="border border-stone-500 px-2 py-1">Full Name</th>
                  <th class="border border-stone-500 px-2 py-1">Email</th>
                  <th class="border border-stone-500 px-2 py-1">Role</th>
                  <th class="border border-stone-500 px-2 py-1">Status</th>
                  <th class="border border-stone-500 px-2 py-1">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="user in usersData" 
                  :key="user.id"
                  class="hover:bg-blue-700 hover:text-white cursor-pointer"
                  :class="!user.is_active ? 'opacity-50 bg-stone-100' : ''"
                >
                  <td class="border border-stone-300 px-2 py-1 font-mono">{{ user.id }}</td>
                  <td class="border border-stone-300 px-2 py-1 font-bold">{{ user.username }}</td>
                  <td class="border border-stone-300 px-2 py-1">{{ user.full_name }}</td>
                  <td class="border border-stone-300 px-2 py-1">{{ user.email }}</td>
                  <td class="border border-stone-300 px-2 py-1">
                    <span 
                      class="px-2 py-0.5 text-xs font-bold rounded"
                      :class="{
                        'bg-red-200 text-red-800': user.role === 'admin',
                        'bg-blue-200 text-blue-800': user.role === 'manager',
                        'bg-stone-200 text-stone-800': user.role === 'user'
                      }"
                    >
                      {{ user.role.toUpperCase() }}
                    </span>
                  </td>
                  <td class="border border-stone-300 px-2 py-1 text-center">
                    <span 
                      class="px-2 py-0.5 text-xs font-bold rounded"
                      :class="user.is_active ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'"
                    >
                      {{ user.is_active ? 'ACTIVE' : 'INACTIVE' }}
                    </span>
                  </td>
                  <td class="border border-stone-300 px-2 py-1">
                    <div class="flex gap-1" v-if="userRole === 'admin'">
                      <button 
                        @click.stop="openUserForm('edit', user, window.id)"
                        class="px-2 py-0.5 bg-blue-500 text-white text-xs font-bold hover:bg-blue-600"
                        title="Edit"
                      >
                        Edit
                      </button>
                      <button 
                        @click.stop="toggleUserStatus(user)"
                        class="px-2 py-0.5 text-xs font-bold"
                        :class="user.is_active ? 'bg-orange-500 text-white hover:bg-orange-600' : 'bg-green-500 text-white hover:bg-green-600'"
                        :title="user.is_active ? 'Deactivate' : 'Activate'"
                      >
                        {{ user.is_active ? 'Deactivate' : 'Activate' }}
                      </button>
                      <button 
                        @click.stop="handleResetPassword(user)"
                        class="px-2 py-0.5 bg-purple-500 text-white text-xs font-bold hover:bg-purple-600"
                        title="Reset Password"
                      >
                        Reset PW
                      </button>
                    </div>
                    <span v-else class="text-stone-400 text-xs">Admin only</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- User Form (Add/Edit) -->
        <div v-else-if="window.content === 'user-form'" class="p-4 bg-stone-200 h-full overflow-auto">
          <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4">
            <h3 class="font-bold text-lg mb-4 border-b border-stone-400 pb-2">
              {{ window.data.mode === 'add' ? 'Create New User' : 'Edit User' }}
            </h3>
            
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Username *</label>
                  <input 
                    v-model="window.data.formData.username" 
                    type="text" 
                    :disabled="window.data.mode === 'edit'"
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                    :class="window.data.mode === 'edit' ? 'bg-stone-200 cursor-not-allowed' : ''"
                    placeholder="Enter username"
                  />
                </div>
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Email *</label>
                  <input 
                    v-model="window.data.formData.email" 
                    type="email" 
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                    placeholder="email@example.com"
                  />
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Full Name *</label>
                  <input 
                    v-model="window.data.formData.full_name" 
                    type="text" 
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                    placeholder="Enter full name"
                  />
                </div>
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Role *</label>
                  <select 
                    v-model="window.data.formData.role"
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                  >
                    <option value="user">User</option>
                    <option value="manager">Manager</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
              
              <div v-if="window.data.mode === 'add'" class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Password *</label>
                  <input 
                    v-model="window.data.formData.password" 
                    type="password" 
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                    placeholder="Min 6 characters"
                  />
                </div>
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Confirm Password *</label>
                  <input 
                    v-model="window.data.formData.confirmPassword" 
                    type="password" 
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                    placeholder="Repeat password"
                  />
                </div>
              </div>
              
              <div v-if="window.data.mode === 'edit'" class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Theme</label>
                  <select 
                    v-model="window.data.formData.theme_preference"
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                  >
                    <option value="RETRO_EARTH">Retro Earth</option>
                    <option value="MODERN_CLEAN">Modern Clean</option>
                    <option value="SPACE_FUTURE">Space Future</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-bold text-stone-700 mb-1">Language</label>
                  <select 
                    v-model="window.data.formData.language"
                    class="w-full bg-white border-2 border-t-stone-600 border-l-stone-600 border-r-stone-100 border-b-stone-100 px-2 py-1 text-sm"
                  >
                    <option value="en">English</option>
                    <option value="th">Thai</option>
                  </select>
                </div>
              </div>
              
              <div v-if="window.data.mode === 'edit'" class="flex items-center gap-2">
                <input 
                  type="checkbox" 
                  id="is_active" 
                  v-model="window.data.formData.is_active"
                  class="w-4 h-4"
                />
                <label for="is_active" class="text-sm font-bold text-stone-700">Active</label>
              </div>
            </div>
            
            <div class="mt-6 flex gap-2 justify-end border-t border-stone-400 pt-4">
              <button 
                @click="closeWindow(window.id)"
                class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm"
              >
                Cancel
              </button>
              <button 
                @click="handleUserSubmit(window.data.formData, window.data.mode, window.id)"
                class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm"
              >
                {{ window.data.mode === 'add' ? 'Create User' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Inventory Menu -->
        <div v-else-if="window.content === 'inventory-menu'" class="p-4 bg-stone-200 h-full">
          <div class="grid grid-cols-3 gap-4">
            <button 
              @click="openInventoryWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Package class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Inventory Management</span>
            </button>
            
            <button 
              @click="handleStockIssue"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Truck class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Stock Issue</span>
            </button>

            <button 
              @click="handleStockReceipt"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <ArrowDown class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Stock Receipt</span>
            </button>

            <button 
              @click="openCycleCountWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Calculator class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Cycle Count</span>
            </button>
          </div>
        </div>

        <!-- Master Data Menu -->
        <div v-else-if="window.content === 'master-menu'" class="p-4 bg-stone-200 h-full">
          <div class="grid grid-cols-3 gap-4">
            <button 
              @click="openItemMasterWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Package class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Item Master</span>
            </button>
            
            <button 
              @click="openPartnersWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Users class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Business Partners Module</span>
            </button>
            
            <button 
              @click="openWarehousesWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Factory class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Warehouses</span>
            </button>

            <button 
              @click="openLocationsWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Factory class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Location Master</span>
            </button>

            <button 
              @click="openBOMMasterWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <FileText class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">BOM Master</span>
            </button>
          </div>
        </div>

        <!-- Factory Settings Menu -->
        <div v-else-if="window.content === 'factory-settings-menu'" class="p-4 bg-stone-200 h-full">
          <div class="grid grid-cols-3 gap-4">
            <button 
              @click="openUserMasterWindow"
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100"
            >
              <Users class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">User Master</span>
            </button>

            <button 
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 opacity-50"
              disabled
            >
              <Settings class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">System Settings</span>
            </button>

            <button 
              class="flex flex-col items-center justify-center p-4 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 hover:bg-stone-200 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 opacity-50"
              disabled
            >
              <Factory class="w-12 h-12 text-stone-700 mb-2" />
              <span class="font-bold text-sm text-center">Factory Config</span>
            </button>
          </div>
        </div>

        <!-- Warehouses Table -->
        <div v-else-if="window.content === 'warehouses-table'" class="h-full flex flex-col">
          <!-- Toolbar -->
          <div class="p-2 bg-stone-300 border-b-2 border-stone-500 flex gap-2">
            <button v-if="userRole === 'admin' || userRole === 'manager'" @click="handleAddWarehouse" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
              + Add Warehouse
            </button>
            <button @click="exportToCSV(filteredWarehouses, 'warehouses.csv')" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
              Export CSV
            </button>
          </div>
          
          <div class="overflow-auto border-2 border-stone-400 bg-white">
            <table class="w-full text-xs border-collapse">
              <thead>
                <tr class="bg-stone-300 border-b-2 border-stone-500">
                  <th 
                    v-for="col in [
                      { key: 'code', label: 'Code', align: 'left' },
                      { key: 'name', label: 'Name', align: 'left' },
                      { key: 'location', label: 'Location', align: 'left' },
                      { key: 'status', label: 'Status', align: 'left' }
                    ]" 
                    :key="col.key"
                    class="border-r border-stone-400 px-2 py-1 font-bold select-none cursor-pointer hover:bg-stone-200 relative"
                    :class="`text-${col.align}`"
                    @click="handleHeaderClick(col.key)"
                    @dblclick.stop="handleHeaderDoubleClick(col.key)"
                  >
                    <div class="flex items-center gap-1" :class="col.align === 'right' ? 'justify-end' : 'justify-start'">
                      <span>{{ col.label }}</span>
                      <div v-if="sortKey === col.key" class="text-stone-600">
                        <ArrowUp v-if="sortOrder === 'asc'" class="w-3 h-3" />
                        <ArrowDown v-else class="w-3 h-3" />
                      </div>
                      <Search v-if="searchFilters[col.key]" class="w-3 h-3 text-olive-600" />
                    </div>
                    
                    <div 
                      v-if="activeSearchColumn === col.key"
                      class="absolute top-full left-0 z-50 bg-stone-200 border-2 border-stone-500 p-1 shadow-lg min-w-[150px]"
                      @click.stop
                    >
                      <input 
                        v-model="searchFilters[col.key]"
                        type="text"
                        class="w-full text-xs px-1 border border-stone-400 outline-none"
                        placeholder="Search..."
                        autoFocus
                      />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(row, idx) in filteredWarehouses" 
                  :key="idx" 
                  :class="idx % 2 === 0 ? 'bg-white' : 'bg-stone-50'"
                  class="hover:bg-blue-100 cursor-pointer"
                  @dblclick="handleRowDoubleClick(row)"
                >
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.code }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.name }}</td>
                  <td class="border-r border-stone-300 px-2 py-1">{{ row.location }}</td>
                  <td class="px-2 py-1">{{ row.status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-1 flex gap-1">
            <div class="h-4 bg-stone-400 border-2 border-stone-500 flex-1"></div>
            <div class="w-4 h-4 bg-stone-400 border-2 border-stone-500"></div>
          </div>
        </div>

        <!-- Warehouse Master Content -->
        <div v-else-if="window.content === 'warehouse-master'" class="p-2 bg-stone-200 h-full overflow-auto">
          <div class="bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 p-4 space-y-4">
            <div class="flex gap-4 items-start">
              <div class="w-24 h-24 bg-white border-2 border-stone-500 flex items-center justify-center">
                <Factory class="w-12 h-12 text-stone-400" />
              </div>
              <div class="flex-1 space-y-2">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-stone-700">Warehouse Code</label>
                    <div class="bg-white border border-stone-500 px-2 py-1 text-sm font-bold">{{ window.data.code }}</div>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-stone-700">Status</label>
                    <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.status }}</div>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Name</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.name }}</div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-stone-700">Location</label>
                  <div class="bg-white border border-stone-500 px-2 py-1 text-sm">{{ window.data.location }}</div>
                </div>
              </div>
            </div>

            <div class="flex justify-between mt-4">
              <div class="flex gap-2" v-if="userRole === 'admin' || userRole === 'manager'">
                <button @click="handleEditWarehouse(window.data)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                  Edit
                </button>
                <button @click="handleDisableWarehouse(window.data)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm text-red-700 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                  Disable
                </button>
              </div>
              <div class="flex gap-2" v-else>
                <div></div>
              </div>

              <button @click="closeWindow(window.id)" class="px-4 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 font-bold text-sm active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400">
                Close
              </button>
            </div>
          </div>
        </div>

        <!-- Item Form -->
        <ItemForm 
          v-else-if="window.content === 'item-form'" 
          :mode="window.data.mode"
          :item="window.data.item"
          @submit="(data) => handleFormSubmit('item', data, window.data.mode, window.id)"
          @cancel="closeWindow(window.id)"
        />

        <!-- Partner Form -->
        <PartnerForm 
          v-else-if="window.content === 'partner-form'" 
          :mode="window.data.mode"
          :partner="window.data.partner"
          @submit="(data) => handleFormSubmit('partner', data, window.data.mode, window.id)"
          @cancel="closeWindow(window.id)"
        />

        <!-- Warehouse Form -->
        <WarehouseForm 
          v-else-if="window.content === 'warehouse-form'" 
          :mode="window.data.mode"
          :warehouse="window.data.warehouse"
          @submit="(data) => handleFormSubmit('warehouse', data, window.data.mode, window.id)"
          @cancel="closeWindow(window.id)"
        />

        <!-- Stock Transaction Form -->
        <StockTransactionForm 
          v-else-if="window.content === 'stock-transaction-form'" 
          :mode="window.data.mode"
          :items="inventoryData"
          :partners="partnersData"
          :warehouses="warehousesData"
          @submit="(data) => handleStockTransactionSubmit(data, window.id)"
          @cancel="closeWindow(window.id)"
        />

        <!-- Location Form -->
        <LocationForm
          v-else-if="window.content === 'location-form'"
          :mode="window.data.mode"
          :initialData="window.data.location"
          :warehouses="warehousesData"
          @submit="(data) => handleLocationSubmit(data, window.data.mode, window.id)"
          @cancel="closeWindow(window.id)"
        />

        <!-- Cycle Count Form -->
        <CycleCountForm
          v-else-if="window.content === 'cycle-count-form'"
          :warehouses="warehousesData"
          @close="closeWindow(window.id)"
        />

        <!-- BOM Master Table -->
        <div v-else-if="window.content === 'bom-table'" class="flex flex-col h-full">
          <!-- Toolbar -->
          <div class="bg-stone-300 border-b-2 border-stone-500 p-1 flex gap-2 flex-wrap items-center">
            <button 
              v-if="userRole === 'admin' || userRole === 'manager'"
              @click="openNewBOMWindow(window.id)"
              class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 text-sm font-bold flex items-center gap-1"
            >
              <div class="w-3 h-3 bg-green-600 border border-stone-500"></div>
              New BOM
            </button>
            <button 
              @click="fetchBOMParents"
              class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 text-sm font-bold flex items-center gap-1"
            >
              <RefreshCw class="w-3 h-3" />
              Refresh
            </button>
            <button 
              @click="exportBOMs(selectedBOMParent ? [selectedBOMParent] : [], true)"
              class="px-3 py-1 bg-stone-300 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 active:border-t-stone-600 active:border-l-stone-600 active:border-r-stone-100 active:border-b-stone-100 active:bg-stone-400 text-sm font-bold flex items-center gap-1"
            >
              Export CSV
            </button>
            <div class="flex-1"></div>
            <!-- Search Fields -->
            <div class="flex gap-1 items-center text-xs">
              <span class="font-bold">Search:</span>
              <input 
                v-model="bomSearchParent"
                type="text" 
                placeholder="Parent item..."
                class="px-2 py-0.5 border-2 border-stone-500 w-32"
              />
              <input 
                v-model="bomSearchChild"
                type="text" 
                placeholder="Child item..."
                class="px-2 py-0.5 border-2 border-stone-500 w-32"
              />
              <button 
                @click="searchBOMs"
                class="px-2 py-0.5 bg-blue-500 text-white font-bold hover:bg-blue-600"
              >
                Go
              </button>
              <button 
                @click="bomSearchParent=''; bomSearchChild=''; fetchBOMParents()"
                class="px-2 py-0.5 bg-stone-400 text-stone-800 font-bold hover:bg-stone-500"
              >
                Clear
              </button>
            </div>
          </div>
          
          <!-- Split View: Parent List + Details -->
          <div class="flex flex-1 overflow-hidden">
            <!-- Parent Items List (Left Panel) -->
            <div class="w-1/3 border-r-2 border-stone-500 flex flex-col">
              <div class="bg-stone-400 px-2 py-1 text-xs font-bold border-b border-stone-500">
                Parent Items (FG/WIP)
              </div>
              <div class="flex-1 bg-white overflow-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead class="bg-stone-300 sticky top-0">
                    <tr>
                      <th class="border border-stone-500 px-2 py-1">Code</th>
                      <th class="border border-stone-500 px-2 py-1">Name</th>
                      <th class="border border-stone-500 px-2 py-1">Rev</th>
                      <th class="border border-stone-500 px-2 py-1">Status</th>
                      <th class="border border-stone-500 px-2 py-1">#</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="parent in bomParentsData" 
                      :key="`${parent.id}-${parent.revision}`"
                      @click="fetchBOMDetails(parent.id, parent.revision)"
                      class="cursor-pointer"
                      :class="selectedBOMParent === parent.id && selectedBOMRevision === parent.revision ? 'bg-blue-700 text-white' : 'hover:bg-blue-100'"
                    >
                      <td class="border border-stone-300 px-2 py-1 font-mono font-bold">{{ parent.item_code }}</td>
                      <td class="border border-stone-300 px-2 py-1 truncate max-w-[120px]" :title="parent.item_name">{{ parent.item_name }}</td>
                      <td class="border border-stone-300 px-2 py-1 text-center font-mono">{{ parent.revision }}</td>
                      <td class="border border-stone-300 px-2 py-1 text-center">
                        <span class="px-1 py-0.5 text-xs rounded" :class="{
                          'bg-green-200 text-green-800': parent.status === 'ACTIVE',
                          'bg-red-200 text-red-800': parent.status === 'INACTIVE'
                        }">
                          {{ parent.status }}
                        </span>
                      </td>
                      <td class="border border-stone-300 px-2 py-1 text-center">{{ parent.component_count }}</td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="bomParentsData.length === 0" class="p-4 text-center text-stone-500 text-sm">
                  No BOMs defined yet. Click "New BOM" to create one.
                </div>
              </div>
            </div>
            
            <!-- BOM Details (Right Panel) -->
            <div class="flex-1 flex flex-col">
              <div class="bg-stone-400 px-2 py-1 text-xs font-bold border-b border-stone-500 flex justify-between items-center">
                <span>BOM Components</span>
                <span v-if="selectedBOMParent" class="text-blue-800">
                  {{ selectedParentLabel || 'Parent selected' }} 
                  <span class="bg-blue-200 text-blue-800 px-1 ml-1 rounded">Rev {{ selectedBOMRevision }}</span>
                </span>
              </div>
              
              <!-- Component Actions with Revision Management -->
              <div v-if="selectedBOMParent" class="bg-stone-200 px-2 py-1 flex gap-2 border-b border-stone-400 flex-wrap items-center">
                <button 
                  v-if="userRole === 'admin' || userRole === 'manager'"
                  @click="openBOMForm('add', selectedBOMParent)"
                  class="px-2 py-0.5 bg-green-500 text-white text-xs font-bold hover:bg-green-600"
                >
                  + Component
                </button>
                <button 
                  v-if="userRole === 'admin' || userRole === 'manager'"
                  @click="createNewRevision(selectedBOMParent, selectedBOMRevision)"
                  class="px-2 py-0.5 bg-blue-500 text-white text-xs font-bold hover:bg-blue-600"
                  title="Copy current revision to create a new one"
                >
                  + New Revision
                </button>
                <button 
                  v-if="(userRole === 'admin' || userRole === 'manager') && bomDetailsData[0]?.status === 'INACTIVE'"
                  @click="setRevisionStatus(selectedBOMParent, selectedBOMRevision, 'ACTIVE')"
                  class="px-2 py-0.5 bg-green-600 text-white text-xs font-bold hover:bg-green-700"
                >
                  Activate
                </button>
                <button 
                  v-if="(userRole === 'admin' || userRole === 'manager') && bomDetailsData[0]?.status === 'ACTIVE'"
                  @click="setRevisionStatus(selectedBOMParent, selectedBOMRevision, 'INACTIVE')"
                  class="px-2 py-0.5 bg-orange-500 text-white text-xs font-bold hover:bg-orange-600"
                >
                  Deactivate
                </button>
                <button 
                  v-if="userRole === 'admin' || userRole === 'manager'"
                  @click="deleteEntireBOM(selectedBOMParent, selectedBOMRevision)"
                  class="px-2 py-0.5 bg-red-500 text-white text-xs font-bold hover:bg-red-600"
                >
                  Delete Rev
                </button>
                <div class="flex-1"></div>
                <span class="text-xs text-stone-600">
                  Status: <span :class="bomDetailsData[0]?.status === 'ACTIVE' ? 'text-green-700 font-bold' : 'text-red-700'">
                    {{ bomDetailsData[0]?.status || 'N/A' }}
                  </span>
                </span>
              </div>
              
              <!-- Component List -->
              <div class="flex-1 bg-white overflow-auto">
                <table v-if="bomDetailsData.length > 0" class="w-full text-left border-collapse text-xs">
                  <thead class="bg-stone-300 sticky top-0">
                    <tr>
                      <th class="border border-stone-500 px-1 py-1">Seq</th>
                      <th class="border border-stone-500 px-1 py-1">Component</th>
                      <th class="border border-stone-500 px-1 py-1">Qty</th>
                      <th class="border border-stone-500 px-1 py-1">UOM</th>
                      <th class="border border-stone-500 px-1 py-1">Scrap%</th>
                      <th class="border border-stone-500 px-1 py-1">Prod Loc</th>
                      <th class="border border-stone-500 px-1 py-1">Stor Loc</th>
                      <th class="border border-stone-500 px-1 py-1">By-Prod</th>
                      <th class="border border-stone-500 px-1 py-1">Remark</th>
                      <th class="border border-stone-500 px-1 py-1" v-if="userRole === 'admin' || userRole === 'manager'">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="line in bomDetailsData" 
                      :key="line.id"
                      class="hover:bg-blue-100"
                      :class="{ 'bg-yellow-50': line.is_byproduct }"
                    >
                      <td class="border border-stone-300 px-1 py-1 text-center font-mono">{{ line.sequence_order }}</td>
                      <td class="border border-stone-300 px-1 py-1">
                        <span class="font-mono font-bold">{{ line.child_item_code }}</span>
                        <span class="text-stone-500 ml-1 truncate max-w-[100px] inline-block" :title="line.child_item_name">{{ line.child_item_name }}</span>
                        <span v-if="line.is_optional" class="ml-1 bg-yellow-200 text-yellow-800 px-1 rounded text-xs">Opt</span>
                      </td>
                      <td class="border border-stone-300 px-1 py-1 text-right font-mono">{{ line.quantity }}</td>
                      <td class="border border-stone-300 px-1 py-1">{{ line.child_uom }}</td>
                      <td class="border border-stone-300 px-1 py-1 text-right">{{ line.scrap_factor }}%</td>
                      <td class="border border-stone-300 px-1 py-1 font-mono text-xs">{{ line.production_location_code || '-' }}</td>
                      <td class="border border-stone-300 px-1 py-1 font-mono text-xs">{{ line.storage_location_code || '-' }}</td>
                      <td class="border border-stone-300 px-1 py-1 text-center">
                        <span v-if="line.is_byproduct" class="text-purple-600 font-bold">Yes</span>
                        <span v-else class="text-stone-400">-</span>
                      </td>
                      <td class="border border-stone-300 px-1 py-1 max-w-[100px] truncate" :title="line.remark">{{ line.remark || '-' }}</td>
                      <td class="border border-stone-300 px-1 py-1" v-if="userRole === 'admin' || userRole === 'manager'">
                        <div class="flex gap-1">
                          <button 
                            @click="openBOMForm('edit', line.parent_item_id, line)"
                            class="px-1 py-0.5 bg-blue-500 text-white text-xs font-bold hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button 
                            @click="deleteBOMLine(line.id, line.parent_item_id)"
                            class="px-1 py-0.5 bg-red-500 text-white text-xs font-bold hover:bg-red-600"
                          >
                            Del
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="p-4 text-center text-stone-500 text-sm">
                  {{ selectedBOMParent ? 'No components in this BOM' : 'Select a parent item to view its BOM' }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- BOM Form Modal (inline at bottom when adding/editing) -->
          <div v-if="bomFormMode === 'add' || editingBOMId !== null" class="border-t-2 border-stone-500 bg-stone-200 p-3 max-h-[300px] overflow-auto">
            <div class="text-sm font-bold mb-2">
              {{ editingBOMId ? 'Edit Component' : 'Add Component' }} - Rev {{ bomFormData.revision }}
            </div>
            <div class="grid grid-cols-6 gap-2 text-xs">
              <!-- Row 1 -->
              <div>
                <label class="block font-bold mb-1">Parent Item</label>
                <input 
                  type="text"
                  class="w-full px-2 py-1 border-2 border-stone-500 text-xs bg-stone-100 font-bold"
                  :value="selectedBOMParent ? selectedParentLabel || 'Loading parent...' : 'Select a parent on the left'"
                  disabled
                />
              </div>
              <div>
                <label class="block font-bold mb-1">Child Item</label>
                <div class="flex gap-1 mb-1">
                  <input
                    type="text"
                    v-model="bomFormData.child_search"
                    class="flex-1 px-2 py-1 border-2 border-stone-500 text-xs"
                    placeholder="Search child item..."
                    :disabled="!bomFormData.parent_item_id"
                  />
                  <button
                    type="button"
                    class="px-2 py-1 bg-stone-300 border-2 border-stone-500 text-xs font-bold disabled:opacity-50"
                    @click="bomFormData.child_search = ''"
                    :disabled="!bomFormData.parent_item_id"
                  >
                    Clear
                  </button>
                </div>
                <select 
                  v-model="bomFormData.child_item_id"
                  class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs disabled:bg-stone-100"
                  :disabled="!bomFormData.parent_item_id"
                >
                  <option :value="null">-- Select --</option>
                  <option
                    v-for="item in filteredChildItems"
                    :key="item._raw?.id || item.id"
                    :value="item._raw?.id || item.id"
                  >
                    {{ item.id }} - {{ item.desc }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">BOM Type</label>
                <select v-model="bomFormData.bom_type" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option value="ASSEMBLY">ASSEMBLY</option>
                  <option value="FORMULA">FORMULA</option>
                  <option value="MODULAR">MODULAR</option>
                  <option value="TAILOR_MADE">TAILOR_MADE</option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Quantity</label>
                <input type="number" v-model="bomFormData.quantity" step="0.0001" min="0" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <div>
                <label class="block font-bold mb-1">Sequence</label>
                <input type="number" v-model="bomFormData.sequence_order" min="0" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <div>
                <label class="block font-bold mb-1">Scrap %</label>
                <input type="number" v-model="bomFormData.scrap_factor" step="0.01" min="0" max="100" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              
              <!-- Row 2: New fields -->
              <div>
                <label class="block font-bold mb-1">Prod Location</label>
                <select v-model="bomFormData.production_location_id" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option :value="null">-- None --</option>
                  <option v-for="loc in bomLocationsData" :key="loc.id" :value="loc.id">
                    {{ loc.location_code }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Storage Location</label>
                <select v-model="bomFormData.storage_location_id" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option :value="null">-- None --</option>
                  <option v-for="loc in bomLocationsData" :key="loc.id" :value="loc.id">
                    {{ loc.location_code }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Status</label>
                <select v-model="bomFormData.status" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="INACTIVE">INACTIVE</option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Active Date</label>
                <input type="date" v-model="bomFormData.active_date" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <div>
                <label class="block font-bold mb-1">Inactive Date</label>
                <input type="date" v-model="bomFormData.inactive_date" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <div class="flex items-center gap-2 pt-4">
                <label class="flex items-center gap-1">
                  <input type="checkbox" v-model="bomFormData.is_optional" class="w-3 h-3"/>
                  <span class="font-bold">Optional</span>
                </label>
                <label class="flex items-center gap-1">
                  <input type="checkbox" v-model="bomFormData.is_byproduct" class="w-3 h-3"/>
                  <span class="font-bold">By-product</span>
                </label>
              </div>
              
              <!-- Row 3: Remark -->
              <div class="col-span-6">
                <label class="block font-bold mb-1">Remark</label>
                <input type="text" v-model="bomFormData.remark" class="w-full px-2 py-1 border-2 border-stone-500 text-xs" placeholder="Additional notes..."/>
              </div>
            </div>
            <div class="flex gap-2 mt-3">
              <button @click="handleBOMSubmit" class="px-4 py-1 bg-green-600 text-white font-bold hover:bg-green-700">
                {{ editingBOMId ? 'Update' : 'Add' }}
              </button>
              <button @click="resetBOMForm(true)" class="px-4 py-1 bg-stone-400 text-stone-800 font-bold hover:bg-stone-500">
                Cancel
              </button>
            </div>
          </div>
        </div>

        <!-- BOM Form (New BOM Creation) -->
        <div v-else-if="window.content === 'bom-form'" class="p-4 space-y-3 overflow-auto">
          <div class="bg-stone-200 p-3 border-2 border-stone-400">
            <div class="text-sm font-bold mb-3">Create New Bill of Materials (Revision {{ bomFormData.revision }})</div>
            <div class="grid grid-cols-3 gap-3 text-sm">
              <!-- Row 1 -->
              <div>
                <label class="block font-bold mb-1">Parent Item (FG/WIP)</label>
                <select v-model="bomFormData.parent_item_id" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option :value="null">-- Select Parent Item --</option>
                  <option v-for="item in inventoryData.filter(i => i._raw && (i._raw.item_type === 'FINISHED_GOOD' || i._raw.item_type === 'WIP'))" :key="item._raw.id" :value="item._raw.id">
                    {{ item.id }} - {{ item.desc }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Component Item</label>
                <select v-model="bomFormData.child_item_id" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option :value="null">-- Select Component --</option>
                  <option v-for="item in inventoryData" :key="item._raw?.id || item.id" :value="item._raw?.id || item.id">
                    {{ item.id }} - {{ item.desc }} ({{ item._raw?.unit_of_measure || 'N/A' }})
                  </option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">BOM Type</label>
                <select v-model="bomFormData.bom_type" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option value="ASSEMBLY">ASSEMBLY - Fixed</option>
                  <option value="FORMULA">FORMULA - Percentage</option>
                  <option value="MODULAR">MODULAR - Options</option>
                  <option value="TAILOR_MADE">TAILOR_MADE - Custom</option>
                </select>
              </div>
              <!-- Row 2 -->
              <div>
                <label class="block font-bold mb-1">Quantity per Parent</label>
                <input type="number" v-model="bomFormData.quantity" step="0.0001" min="0" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <div>
                <label class="block font-bold mb-1">Sequence Order</label>
                <input type="number" v-model="bomFormData.sequence_order" min="0" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <div>
                <label class="block font-bold mb-1">Scrap Factor (%)</label>
                <input type="number" v-model="bomFormData.scrap_factor" step="0.01" min="0" max="100" class="w-full px-2 py-1 border-2 border-stone-500 text-xs"/>
              </div>
              <!-- Row 3: New fields -->
              <div>
                <label class="block font-bold mb-1">Production Location</label>
                <select v-model="bomFormData.production_location_id" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option :value="null">-- None --</option>
                  <option v-for="loc in bomLocationsData" :key="loc.id" :value="loc.id">{{ loc.location_code }}</option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Storage Location</label>
                <select v-model="bomFormData.storage_location_id" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option :value="null">-- None --</option>
                  <option v-for="loc in bomLocationsData" :key="loc.id" :value="loc.id">{{ loc.location_code }}</option>
                </select>
              </div>
              <div>
                <label class="block font-bold mb-1">Status</label>
                <select v-model="bomFormData.status" class="w-full px-2 py-1 border-2 border-stone-500 bg-white text-xs">
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="INACTIVE">INACTIVE</option>
                </select>
              </div>
              <!-- Row 4 -->
              <div class="col-span-2">
                <label class="block font-bold mb-1">Remark</label>
                <input type="text" v-model="bomFormData.remark" class="w-full px-2 py-1 border-2 border-stone-500 text-xs" placeholder="Additional notes..."/>
              </div>
              <div class="flex items-center gap-3 pt-4">
                <label class="flex items-center gap-1">
                  <input type="checkbox" v-model="bomFormData.is_optional" class="w-4 h-4"/>
                  <span class="font-bold">Optional</span>
                </label>
                <label class="flex items-center gap-1">
                  <input type="checkbox" v-model="bomFormData.is_byproduct" class="w-4 h-4"/>
                  <span class="font-bold">By-product</span>
                </label>
              </div>
            </div>
            <div class="flex gap-2 mt-4">
              <button @click="handleBOMSubmit" class="px-4 py-1 bg-green-600 text-white font-bold hover:bg-green-700">Create BOM</button>
              <button @click="closeWindow(window.id)" class="px-4 py-1 bg-stone-400 text-stone-800 font-bold hover:bg-stone-500">Cancel</button>
            </div>
          </div>
          <div class="bg-white p-3 border border-stone-400 text-xs">
            <p class="font-bold mb-1">BOM Type Guide:</p>
            <ul class="list-disc list-inside text-stone-600 space-y-1">
              <li><strong>ASSEMBLY:</strong> Fixed quantity of each component</li>
              <li><strong>FORMULA:</strong> Percentage-based (e.g., recipes, mixtures)</li>
              <li><strong>MODULAR:</strong> Has optional components</li>
              <li><strong>TAILOR_MADE:</strong> Customized per work order</li>
            </ul>
          </div>
        </div>

        <!-- Production Plan Calendar -->
        <div v-else-if="window.content === 'production-plan-calendar'" class="h-full bg-stone-200">
          <ProductionPlanCalendar />
        </div>

        <div v-else class="p-4 space-y-2">
          <div class="bg-white border-2 border-stone-400 p-3">
            <p class="text-sm text-stone-800">Module: {{ window.title }}</p>
          </div>
        </div>

        <!-- Resize Handle -->
        <div 
          v-if="!window.maximized"
          class="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize z-50 flex items-end justify-end p-0.5"
          @mousedown.stop.prevent="(e) => handleResizeStart(e, window.id)"
        >
          <div class="w-0 h-0 border-b-[8px] border-r-[8px] border-b-stone-500 border-r-transparent transform rotate-0"></div>
        </div>
      </div>
    </div>

    <!-- Taskbar -->
    <div class="absolute bottom-0 left-0 right-0 h-12 bg-stone-400 border-t-4 border-t-stone-100 border-b-2 border-b-stone-600 flex items-center px-2 gap-2 shadow-2xl z-[100]">
      <div class="relative">
        <button 
          @click.stop="showStartMenu = !showStartMenu"
          class="bg-stone-300 hover:bg-stone-200 border-2 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 px-3 py-1 flex items-center gap-2 font-bold text-sm"
        >
          <div class="w-4 h-4 bg-red-700 border border-stone-500"></div>
          START
        </button>

        <!-- Start Menu -->
        <div 
          v-if="showStartMenu"
          class="absolute bottom-full left-0 mb-1 bg-stone-300 border-4 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600 shadow-2xl w-[200px]"
          @click.stop
        >
          <div class="bg-gradient-to-r from-olive-700 to-olive-600 text-stone-100 px-3 py-2 border-b-2 border-stone-500">
            <div class="font-bold text-sm">ERP System</div>
            <div class="text-xs opacity-90">Windows 3.11</div>
          </div>
          <div class="p-1">
            <button class="w-full text-left px-3 py-2 hover:bg-olive-700 hover:text-white text-sm font-bold flex items-center gap-2 border-b border-stone-400">
              <Users class="w-4 h-4" />
              Profile
            </button>
            <button class="w-full text-left px-3 py-2 hover:bg-olive-700 hover:text-white text-sm font-bold flex items-center gap-2 border-b border-stone-400">
              <Settings class="w-4 h-4" />
              {{ $t('common.settings') || 'Settings' }}
            </button>
            <button class="w-full text-left px-3 py-2 hover:bg-olive-700 hover:text-white text-sm font-bold flex items-center gap-2 border-b border-stone-400">
              <HelpCircle class="w-4 h-4" />
              Help
            </button>
            <button 
              @click="handleLogout"
              class="w-full text-left px-3 py-2 hover:bg-red-600 hover:text-white text-sm font-bold flex items-center gap-2 text-red-700"
            >
              <X class="w-4 h-4" />
              {{ $t('common.logout') }}
            </button>
          </div>
        </div>
      </div>
      
      <div class="flex-1 flex gap-1 overflow-x-auto">
        <button
          v-for="window in windows"
          :key="window.id"
          @click="window.minimized ? restoreWindow(window.id) : bringToFront(window.id)"
          class="px-3 py-1 text-xs font-bold border-2 truncate max-w-[150px]"
          :class="[
            window.minimized 
              ? 'bg-stone-400 border-stone-500'
              : 'bg-stone-300 border-t-stone-100 border-l-stone-100 border-r-stone-600 border-b-stone-600'
          ]"
        >
          [{{ window.title }}]
        </button>
      </div>

      <button 
        @click="showCalendar = !showCalendar"
        class="bg-stone-300 border-2 border-stone-500 px-3 py-1 text-xs font-bold hover:bg-stone-200 flex flex-col items-center min-w-[80px]"
        :class="{ 'bg-stone-200': showCalendar }"
      >
        <div>{{ formattedTime }}</div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Package, Truck, Settings, FileText, Factory, Calculator, Folder, BarChart3, HelpCircle, Edit, Users, X, Search, ArrowUp, ArrowDown, RefreshCw, Shield, UserPlus, KeyRound } from 'lucide-vue-next'
import LoginScreen from './components/LoginScreen.vue'
import ItemForm from './components/ItemForm.vue'
import PartnerForm from './components/PartnerForm.vue'
import WarehouseForm from './components/WarehouseForm.vue'
import StockTransactionForm from './components/StockTransactionForm.vue'
import LocationForm from './components/LocationForm.vue'
import CycleCountForm from './components/CycleCountForm.vue'
import ProductionPlanCalendar from './components/ProductionPlanCalendar.vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()

// --- Timezone & DateTime Utilities ---
// Get client's timezone offset in minutes from UTC (e.g., +420 for UTC+7)
const getTimezoneOffset = () => -new Date().getTimezoneOffset()  // Note: JS getTimezoneOffset returns opposite sign

// Create axios instance with default headers including timezone
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-Client-Timezone-Offset': getTimezoneOffset().toString()
  }
})

// Format UTC datetime to local time for display
const formatDateTimeLocal = (utcDateString) => {
  if (!utcDateString) return '-'
  const date = new Date(utcDateString)
  return date.toLocaleString('th-TH', { 
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false 
  })
}

// Format UTC datetime to local date only
const formatDateLocal = (utcDateString) => {
  if (!utcDateString) return '-'
  const date = new Date(utcDateString)
  return date.toLocaleDateString('th-TH')
}

// Get current local datetime in ISO format for sending to backend
const getLocalDateTimeISO = () => {
  const now = new Date()
  return now.toISOString()
}

// Helper to get headers with auth token and timezone offset
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    Authorization: `Bearer ${token}`,
    'X-Client-Timezone-Offset': getTimezoneOffset().toString()
  }
}

// --- State ---
const isLoggedIn = ref(false)
const userRole = ref('')
const icons = ref([
  { id: 'inventory', nameKey: 'desktop.inventory', icon: Package, x: 30, y: 30 },
  { id: 'delivery', nameKey: 'desktop.sales', icon: Truck, x: 130, y: 30 },
  { id: 'master', nameKey: 'desktop.master', icon: Settings, x: 30, y: 130 },
  { id: 'purchase', nameKey: 'desktop.purchase', icon: FileText, x: 130, y: 130 },
  { id: 'production', nameKey: 'Production Planning', icon: Factory, x: 30, y: 230 },
  { id: 'mrp', nameKey: 'desktop.mrp', icon: Calculator, x: 130, y: 230 },
  { id: 'settings', nameKey: 'desktop.settings', icon: Settings, x: 30, y: 330 },
  { id: 'reports', nameKey: 'desktop.appMarket', icon: BarChart3, x: 130, y: 330 },
  { id: 'folder1', nameKey: '', icon: Folder, x: 30, y: 460 },
  { id: 'folder2', nameKey: '', icon: Folder, x: 130, y: 460 },
  { id: 'help', nameKey: '', icon: HelpCircle, x: 30, y: 540 },
  { id: 'edit', nameKey: '', icon: Edit, x: 130, y: 540 },
])

const windows = ref([])
const draggedIcon = ref(null)
const draggedWindow = ref(null)
const resizingWindow = ref(null)
const nextZIndex = ref(10)
const currentTime = ref(new Date())
const showCalendar = ref(true)
const showStartMenu = ref(false)
const calendarMonth = ref(10) // November
const calendarYear = ref(2025)

const events = ref([
  { month: 10, date: 1, title: 'รับสินค้า Vendor A', type: 'receive', color: 'bg-blue-500' },
  { month: 10, date: 5, title: 'ส่งออเดอร์ #1234', type: 'delivery', color: 'bg-green-600' },
  { month: 10, date: 12, title: 'รับสินค้า Vendor B', type: 'receive', color: 'bg-blue-500' },
  { month: 10, date: 15, title: 'ส่งออเดอร์ #1567', type: 'delivery', color: 'bg-green-600' },
  { month: 10, date: 20, title: 'จ่ายเงิน Supplier', type: 'payment', color: 'bg-amber-600' },
  { month: 10, date: 24, title: 'ส่งออเดอร์ #1890', type: 'delivery', color: 'bg-green-600' },
  { month: 10, date: 28, title: 'ตรวจนับสต็อก', type: 'inventory', color: 'bg-purple-600' },
  { month: 11, date: 5, title: 'รับสินค้า Vendor C', type: 'receive', color: 'bg-blue-500' },
  { month: 11, date: 15, title: 'ส่งออเดอร์ #2000', type: 'delivery', color: 'bg-green-600' },
  { month: 9, date: 25, title: 'ตรวจนับสต็อก Q4', type: 'inventory', color: 'bg-purple-600' },
])

// Data arrays
const inventoryData = ref([])
const partnersData = ref([])
const warehousesData = ref([])
const locationsData = ref([])
const usersData = ref([])
const userStats = ref({ total_users: 0, active_users: 0, inactive_users: 0, by_role: {} })

// BOM data
const bomParentsData = ref([])  // List of parent items with BOMs
const bomDetailsData = ref([])  // BOM details for selected parent
const selectedBOMParent = ref(null)  // Currently selected parent item
const selectedBOMRevision = ref(null)  // Currently selected revision
const bomLocationsData = ref([])  // Locations for production/storage selection
const bomSearchParent = ref('')  // Search filter for parent items
const bomSearchChild = ref('')  // Search filter for child items
const bomFormData = ref({
  parent_item_id: null,
  child_item_id: null,
  bom_type: 'ASSEMBLY',
  is_template: true,
  sequence_order: 0,
  quantity: 1,
  percentage: null,
  is_optional: false,
  scrap_factor: 0,
  production_location_id: null,
  storage_location_id: null,
  is_byproduct: false,
  remark: '',
  revision: 1,
  status: 'ACTIVE',
  active_date: null,
  inactive_date: null,
  child_search: ''
})
const bomFormMode = ref('add')  // 'add' or 'edit'
const editingBOMId = ref(null)
const bomExportSelection = ref([])  // Selected items for export

// Table state
const searchFilters = ref({})
const sortKey = ref('')
const sortOrder = ref('asc')
const activeSearchColumn = ref(null)

const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const monthNamesTH = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']

// --- Computed ---
const formattedDate = computed(() => currentTime.value.toLocaleDateString('th-TH', { day: '2-digit', month: 'short', year: 'numeric' }))
const formattedTime = computed(() => currentTime.value.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }))
const daysInMonth = computed(() => new Date(calendarYear.value, calendarMonth.value + 1, 0).getDate())
const firstDay = computed(() => new Date(calendarYear.value, calendarMonth.value, 1).getDay())
const monthEvents = computed(() => events.value.filter(e => e.month === calendarMonth.value))

const filteredChildItems = computed(() => {
  const parentId = bomFormData.value.parent_item_id || selectedBOMParent.value
  if (!parentId) return []
  const searchTerm = (bomFormData.value.child_search || '').toLowerCase()
  return inventoryData.value.filter(item => {
    const itemId = item._raw?.id || item.id
    if (itemId === parentId) return false
    if (!searchTerm) return true
    const label = `${item.id || ''} ${item.desc || ''}`.toLowerCase()
    return label.includes(searchTerm)
  })
})

const selectedParentLabel = computed(() => {
  if (!selectedBOMParent.value) return ''
  const detail = bomDetailsData.value[0]
  if (detail) {
    return `${detail.parent_item_code || ''} - ${detail.parent_item_name || ''}`.trim()
  }
  const fallback = bomParentsData.value.find(parent => parent.id === selectedBOMParent.value)
  if (fallback) {
    return `${fallback.item_code || ''} - ${fallback.item_name || ''}`.trim()
  }
  return ''
})

const filteredInventory = computed(() => {
  let result = [...inventoryData.value]

  // Filter
  Object.keys(searchFilters.value).forEach(key => {
    const term = searchFilters.value[key].toLowerCase()
    if (term) {
      result = result.filter(item => 
        String(item[key]).toLowerCase().includes(term)
      )
    }
  })

  // Sort
  if (sortKey.value) {
    result.sort((a, b) => {
      let modifier = sortOrder.value === 'asc' ? 1 : -1
      if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier
      if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier
      return 0
    })
  }

  return result
})

watch(selectedBOMParent, (newParent) => {
  if (editingBOMId.value !== null) return
  if (!newParent) {
    bomFormData.value.parent_item_id = null
    bomFormData.value.child_item_id = null
    bomFormData.value.child_search = ''
    return
  }
  bomFormData.value.parent_item_id = newParent
  bomFormData.value.revision = selectedBOMRevision.value || bomFormData.value.revision || 1
  bomFormData.value.child_item_id = null
  bomFormData.value.child_search = ''
})

watch(selectedBOMRevision, (newRevision) => {
  if (editingBOMId.value !== null) return
  if (newRevision) {
    bomFormData.value.revision = newRevision
  }
})

const filteredPartners = computed(() => {
  let result = [...partnersData.value]

  // Filter
  Object.keys(searchFilters.value).forEach(key => {
    const term = searchFilters.value[key].toLowerCase()
    if (term) {
      result = result.filter(item => 
        String(item[key]).toLowerCase().includes(term)
      )
    }
  })

  // Sort
  if (sortKey.value) {
    result.sort((a, b) => {
      let modifier = sortOrder.value === 'asc' ? 1 : -1
      if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier
      if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier
      return 0
    })
  }

  return result
})

const filteredWarehouses = computed(() => {
  let result = [...warehousesData.value]

  // Filter
  Object.keys(searchFilters.value).forEach(key => {
    const term = searchFilters.value[key].toLowerCase()
    if (term) {
      result = result.filter(item => 
        String(item[key]).toLowerCase().includes(term)
      )
    }
  })

  // Sort
  if (sortKey.value) {
    result.sort((a, b) => {
      let modifier = sortOrder.value === 'asc' ? 1 : -1
      if (a[sortKey.value] < b[sortKey.value]) return -1 * modifier
      if (a[sortKey.value] > b[sortKey.value]) return 1 * modifier
      return 0
    })
  }

  return result
})

// --- Methods ---
async function fetchInventory() {
  try {
    const response = await axios.get('http://localhost:8000/api/items', {
      headers: getAuthHeaders()
    })
    inventoryData.value = response.data.map(item => ({
      id: item.item_code,
      desc: item.item_name,
      category: item.item_type,
      qty: 0, // TODO: Fetch from InventoryBalance
      reorder: item.reorder_point,
      status: item.is_active ? 'Active' : 'Inactive',
      // Store full object for Item Master
      _raw: item
    }))
  } catch (error) {
    console.error('Failed to fetch inventory:', error)
  }
}

async function fetchPartners() {
  try {
    const response = await axios.get('http://localhost:8000/api/partners', {
      headers: getAuthHeaders()
    })
    partnersData.value = response.data.map(item => ({
      code: item.partner_code,
      name: item.partner_name,
      type: item.partner_type,
      taxId: item.tax_id,
      phone: item.phone,
      email: item.email,
      status: item.is_active ? 'Active' : 'Inactive',
      _raw: item
    }))
  } catch (error) {
    console.error('Failed to fetch partners:', error)
  }
}

async function fetchWarehouses() {
  try {
    const response = await axios.get('http://localhost:8000/api/warehouses', {
      headers: getAuthHeaders()
    })
    warehousesData.value = response.data.map(item => ({
      id: item.id,
      code: item.warehouse_code,
      name: item.warehouse_name,
      location: item.location,
      status: item.is_active ? 'Active' : 'Inactive',
      _raw: item
    }))
  } catch (error) {
    console.error('Failed to fetch warehouses:', error)
  }
}

async function fetchLocations() {
  try {
    const response = await axios.get('http://localhost:8000/api/wms/locations', {
      headers: getAuthHeaders()
    })
    locationsData.value = response.data.map(item => ({
      id: item.id,
      warehouse_id: item.warehouse_id,
      location_code: item.location_code,
      zone_type: item.zone_type,
      condition_type: item.condition_type,
      is_secure_cage: item.is_secure_cage,
      floor_level: item.floor_level,
      security_level: item.security_level,
      capacity_cbm: item.capacity_cbm,
      _raw: item
    }))
  } catch (error) {
    console.error('Failed to fetch locations:', error)
  }
}

async function fetchUsers() {
  try {
    const response = await axios.get('http://localhost:8000/api/users', {
      headers: getAuthHeaders()
    })
    usersData.value = response.data.map(user => ({
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      theme_preference: user.theme_preference,
      language: user.language,
      is_active: user.is_active,
      created_at: formatDateTimeLocal(user.created_at),  // Format UTC to local time
      _raw: user
    }))
    
    // Fetch user stats
    const statsResponse = await axios.get('http://localhost:8000/api/users/stats/summary', {
      headers: getAuthHeaders()
    })
    userStats.value = statsResponse.data
  } catch (error) {
    console.error('Failed to fetch users:', error)
    if (error.response?.status === 403) {
      alert('Access denied. Admin privileges required.')
    }
  }
}

function handleHeaderClick(key) {
  if (activeSearchColumn.value === key) {
    activeSearchColumn.value = null
  } else {
    activeSearchColumn.value = key
    // Initialize filter if not exists
    if (!searchFilters.value[key]) searchFilters.value[key] = ''
  }
}

function handleHeaderDoubleClick(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

function handleRowDoubleClick(item) {
  if (item.id) {
    // Item Master
    openWindow(`item-${item.id}`, `Item Master: ${item.id}`, 'item-master', item)
  } else if (item.code && item.type) {
    // Partner Master
    openWindow(`partner-${item.code}`, `Partner Master: ${item.code}`, 'partner-master', item)
  } else if (item.code && item.location) {
    // Warehouse Master
    openWindow(`warehouse-${item.code}`, `Warehouse Master: ${item.code}`, 'warehouse-master', item)
  }
}

function changeMonth(step) {
  let newMonth = calendarMonth.value + step
  let newYear = calendarYear.value
  
  if (newMonth > 11) {
    newMonth = 0
    newYear++
  } else if (newMonth < 0) {
    newMonth = 11
    newYear--
  }
  
  calendarMonth.value = newMonth
  calendarYear.value = newYear
}

function isToday(date) {
  const today = new Date()
  return date === today.getDate() && 
         calendarMonth.value === today.getMonth() && 
         calendarYear.value === today.getFullYear()
}

function getEvent(date) {
  return monthEvents.value.find(e => e.date === date)
}

function handleLoginSuccess(data) {
  console.log('App.vue: handleLoginSuccess called with data:', data)
  console.log('App.vue: data.user:', data.user)
  isLoggedIn.value = true
  if (data.user && data.user.role) {
    userRole.value = data.user.role
    console.log('App.vue: User role set to:', userRole.value)
  } else {
    console.warn('App.vue: No user role found in login response!')
  }
  console.log('App.vue: Final userRole value:', userRole.value)
}

function handleIconDragStart(e, iconId) {
  draggedIcon.value = iconId
  e.dataTransfer.effectAllowed = 'move'
  // Hide ghost image
  const img = new Image()
  img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
  e.dataTransfer.setDragImage(img, 0, 0)
}

function handleIconDrag(e, iconId) {
  if (e.clientX === 0 && e.clientY === 0) return
  const icon = icons.value.find(i => i.id === iconId)
  if (icon) {
    icon.x = e.clientX - 40
    icon.y = e.clientY - 50
  }
}

function handleIconDragEnd() {
  draggedIcon.value = null
}

function handleIconDoubleClick(icon) {
  if (icon.id === 'inventory') {
    openWindow(icon.id, t('desktop.inventory'), 'inventory-menu')
  } else if (icon.id === 'master') {
    openWindow(icon.id, t('desktop.master'), 'master-menu')
  } else if (icon.id === 'settings') {
    openWindow(icon.id, 'Factory Settings', 'factory-settings-menu')
  } else if (icon.id === 'production') {
    openWindow(icon.id, '📅 Production Planning Calendar', 'production-plan-calendar')
  } else {
    openWindow(icon.id, icon.nameKey ? t(icon.nameKey) : '', 'default')
  }
}

function openItemMasterWindow() {
  fetchInventory()
  openWindow('items-list', 'Item Master Module', 'items-table', { allowAdd: true })
}

function openInventoryWindow() {
  fetchInventory()
  openWindow('inventory-list', 'Inventory Management', 'items-table', { allowAdd: false })
}

function openPartnersWindow() {
  fetchPartners()
  openWindow('partners-list', 'Business Partners Module', 'partners-table')
}

function openWarehousesWindow() {
  fetchWarehouses()
  openWindow('warehouses-list', 'Warehouse Master Module', 'warehouses-table')
}

function openWindow(iconId, title, content, data = null) {
  const existingWindow = windows.value.find(w => w.id === iconId)
  if (existingWindow) {
    bringToFront(iconId)
    if (existingWindow.minimized) existingWindow.minimized = false
    return
  }

  windows.value.push({
    id: iconId,
    title: title,
    content: content,
    data: data,
    x: 250 + windows.value.length * 30,
    y: 250 + windows.value.length * 30,
    width: 650,
    height: 400,
    minimized: false,
    maximized: false,
    zIndex: nextZIndex.value++
  })
}

function closeWindow(id) {
  windows.value = windows.value.filter(w => w.id !== id)
}

function minimizeWindow(id) {
  const window = windows.value.find(w => w.id === id)
  if (window) window.minimized = true
}

function restoreWindow(id) {
  const window = windows.value.find(w => w.id === id)
  if (window) {
    window.minimized = false
    bringToFront(id)
  }
}

function toggleMaximize(id) {
  const window = windows.value.find(w => w.id === id)
  if (window) {
    window.maximized = !window.maximized
    bringToFront(id)
  }
}

function bringToFront(id) {
  const window = windows.value.find(w => w.id === id)
  if (window) window.zIndex = nextZIndex.value++
}

function handleWindowMouseDown(e, windowId) {
  bringToFront(windowId)
  // Check if clicking titlebar
  if (e.target.closest('.window-titlebar')) {
    const window = windows.value.find(w => w.id === windowId)
    if (!window.maximized) {
      draggedWindow.value = {
        id: windowId,
        startX: e.clientX - window.x,
        startY: e.clientY - window.y
      }
    }
  }
}

function handleResizeStart(e, windowId) {
  const window = windows.value.find(w => w.id === windowId)
  if (window && !window.maximized) {
    resizingWindow.value = {
      id: windowId,
      startX: e.clientX,
      startY: e.clientY,
      startWidth: window.width,
      startHeight: window.height
    }
  }
}

function handleMouseMove(e) {
  if (draggedWindow.value) {
    const window = windows.value.find(w => w.id === draggedWindow.value.id)
    if (window && !window.maximized) {
      window.x = e.clientX - draggedWindow.value.startX
      window.y = e.clientY - draggedWindow.value.startY
    }
  } else if (resizingWindow.value) {
    const window = windows.value.find(w => w.id === resizingWindow.value.id)
    if (window) {
      const dx = e.clientX - resizingWindow.value.startX
      const dy = e.clientY - resizingWindow.value.startY
      window.width = Math.max(300, resizingWindow.value.startWidth + dx)
      window.height = Math.max(200, resizingWindow.value.startHeight + dy)
    }
  }
}

function handleMouseUp() {
  draggedWindow.value = null
  resizingWindow.value = null
}

function handleLogout() {
  if (confirm(t('common.logout') + '?')) {
    localStorage.removeItem('token')
    isLoggedIn.value = false
    showStartMenu.value = false
  }
}

// Form submission handler
async function handleFormSubmit(type, formData, mode, windowId) {
  let success = false
  
  if (type === 'item') {
    success = await saveItem(formData, mode)
  } else if (type === 'partner') {
    success = await savePartner(formData, mode)
  } else if (type === 'warehouse') {
    success = await saveWarehouse(formData, mode)
  }
  
  if (success) {
    closeWindow(windowId)
  }
}

// CRUD Handlers for Items
function handleAddItem() {
  openWindow('add-item', 'Add New Item', 'item-form', { mode: 'add', type: 'item' })
}

function handleEditItem(item) {
  openWindow(`edit-item-${item.id}`, `Edit Item: ${item.id}`, 'item-form', { mode: 'edit', type: 'item', item })
}

async function handleDisableItem(item) {
  if (!confirm(`Disable item "${item.id}"?`)) return
  
  try {
    await axios.delete(`http://localhost:8000/api/items/${item.id}`, {
      headers: getAuthHeaders()
    })
    alert('Item disabled successfully!')
    fetchInventory() // Refresh list
    closeWindow(`item-${item.id}`) // Close detail window
  } catch (error) {
    console.error('Failed to disable item:', error)
    alert(parseApiError(error, 'Item'))
  }
}

// Helper function to parse API errors and return user-friendly messages
function parseApiError(error, entityType = 'record') {
  const detail = error.response?.data?.detail || ''
  const status = error.response?.status
  
  // Check for duplicate/unique constraint errors
  if (detail.includes('UNIQUE constraint failed') || detail.includes('duplicate key') || detail.includes('already exists')) {
    if (detail.includes('item_code')) {
      return `Item Code already exists. Please use a different code.`
    }
    if (detail.includes('partner_code')) {
      return `Partner Code already exists. Please use a different code.`
    }
    if (detail.includes('warehouse_code')) {
      return `Warehouse Code already exists. Please use a different code.`
    }
    if (detail.includes('username')) {
      return `Username already exists. Please choose a different username.`
    }
    if (detail.includes('email')) {
      return `Email already exists. Please use a different email address.`
    }
    return `This ${entityType} code already exists. Please use a different code.`
  }
  
  // Check for not found errors
  if (status === 404 || detail.includes('not found')) {
    return `${entityType} not found. It may have been deleted.`
  }
  
  // Check for authentication errors
  if (status === 401) {
    return `Session expired. Please login again.`
  }
  
  // Check for permission errors
  if (status === 403) {
    return `You don't have permission to perform this action.`
  }
  
  // Check for validation errors
  if (status === 422 || detail.includes('validation')) {
    return `Invalid data. Please check your input and try again.`
  }
  
  // Check for required field errors
  if (detail.includes('required') || detail.includes('null') || detail.includes('NOT NULL')) {
    return `Please fill in all required fields.`
  }
  
  // Default error message
  return detail || `Failed to save ${entityType}. Please try again.`
}

async function saveItem(formData, mode) {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    
    if (mode === 'add') {
      await axios.post('http://localhost:8000/api/items/', formData, { headers })
      alert('Item created successfully!')
    } else {
      await axios.put(`http://localhost:8000/api/items/${formData.item_code}`, formData, { headers })
      alert('Item updated successfully!')
    }
    
    fetchInventory() // Refresh list
    return true
  } catch (error) {
    console.error('Failed to save item:', error)
    alert(parseApiError(error, 'Item'))
    return false
  }
}

// CRUD Handlers for Partners
function handleAddPartner() {
  openWindow('add-partner', 'Add New Partner', 'partner-form', { mode: 'add', type: 'partner' })
}

function handleEditPartner(partner) {
  openWindow(`edit-partner-${partner.code}`, `Edit Partner: ${partner.code}`, 'partner-form', { mode: 'edit', type: 'partner', partner })
}

async function handleDisablePartner(partner) {
  if (!confirm(`Disable partner "${partner.code}"?`)) return
  
  try {
    await axios.delete(`http://localhost:8000/api/partners/${partner.code}`, {
      headers: getAuthHeaders()
    })
    alert('Partner disabled successfully!')
    fetchPartners() // Refresh list
    closeWindow(`partner-${partner.code}`) // Close detail window
  } catch (error) {
    console.error('Failed to disable partner:', error)
    alert(parseApiError(error, 'Partner'))
  }
}

async function savePartner(formData, mode) {
  try {
    const headers = getAuthHeaders()
    
    if (mode === 'add') {
      await axios.post('http://localhost:8000/api/partners/', formData, { headers })
      alert('Partner created successfully!')
    } else {
      await axios.put(`http://localhost:8000/api/partners/${formData.partner_code}`, formData, { headers })
      alert('Partner updated successfully!')
    }
    
    fetchPartners() // Refresh list
    return true
  } catch (error) {
    console.error('Failed to save partner:', error)
    alert(parseApiError(error, 'Partner'))
    return false
  }
}

// CRUD Handlers for Warehouses
function handleAddWarehouse() {
  openWindow('add-warehouse', 'Add New Warehouse', 'warehouse-form', { mode: 'add', type: 'warehouse' })
}

function handleEditWarehouse(warehouse) {
  openWindow(`edit-warehouse-${warehouse.code}`, `Edit Warehouse: ${warehouse.code}`, 'warehouse-form', { mode: 'edit', type: 'warehouse', warehouse })
}

async function handleDisableWarehouse(warehouse) {
  if (!confirm(`Disable warehouse "${warehouse.code}"?`)) return
  
  try {
    await axios.delete(`http://localhost:8000/api/warehouses/${warehouse.code}`, {
      headers: getAuthHeaders()
    })
    alert('Warehouse disabled successfully!')
    fetchWarehouses() // Refresh list
    closeWindow(`warehouse-${warehouse.code}`) // Close detail window
  } catch (error) {
    console.error('Failed to disable warehouse:', error)
    alert(parseApiError(error, 'Warehouse'))
  }
}

async function saveWarehouse(formData, mode) {
  try {
    const headers = getAuthHeaders()
    
    if (mode === 'add') {
      await axios.post('http://localhost:8000/api/warehouses/', formData, { headers })
      alert('Warehouse created successfully!')
    } else {
      await axios.put(`http://localhost:8000/api/warehouses/${formData.warehouse_code}`, formData, { headers })
      alert('Warehouse updated successfully!')
    }
    
    fetchWarehouses() // Refresh list
    return true
  } catch (error) {
    console.error('Failed to save warehouse:', error)
    alert(parseApiError(error, 'Warehouse'))
    return false
  }
}

function exportToCSV(data, filename) {
  if (!data || !data.length) {
    alert('No data to export')
    return
  }

  // Get headers from first object
  const headers = Object.keys(data[0]).filter(key => key !== '_raw')
  
  // Create CSV content
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => {
      const val = row[header]
      return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val
    }).join(','))
  ].join('\n')

  // Create download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// Inventory Transactions
function handleStockIssue() {
  openWindow('stock-issue', 'Stock Issue (Out)', 'stock-transaction-form', { mode: 'issue' })
}

function handleStockReceipt() {
  openWindow('stock-receipt', 'Stock Receipt (In)', 'stock-transaction-form', { mode: 'receipt' })
}

async function handleStockTransactionSubmit(data, windowId) {
  try {
    await axios.post('http://localhost:8000/api/inventory/transactions', data, {
      headers: getAuthHeaders()
    })
    alert('Transaction recorded successfully')
    fetchInventory()
    closeWindow(windowId)
  } catch (error) {
    console.error('Failed to record transaction:', error)
    alert(error.response?.data?.detail || 'Failed to record transaction')
  }
}

// WMS Handlers
function getWarehouseName(id) {
  const w = warehousesData.value.find(w => w.id === id)
  return w ? w.name : id
}

async function handleLocationSubmit(data, mode, windowId) {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    
    if (mode === 'add') {
      await axios.post('http://localhost:8000/api/wms/locations', data, { headers })
      alert('Location created successfully!')
    } else {
      await axios.put(`http://localhost:8000/api/wms/locations/${data.id}`, data, { headers })
      alert('Location updated successfully!')
    }
    fetchLocations()
    closeWindow(windowId)
  } catch (error) {
    console.error("Failed to save location", error)
    alert(parseApiError(error, 'Location'))
  }
}

function openLocationForm(mode, location = null, parentWindowId) {
  const title = mode === 'add' ? 'Add Location' : `Edit Location ${location.location_code}`
  openWindow(`location-form-${Date.now()}`, title, 'location-form', { mode, location })
}

function openLocationsWindow() {
  fetchWarehouses() // Fetch warehouses first for the dropdown
  fetchLocations()
  openWindow('locations-list', 'Warehouse Locations', 'locations-table')
}

function openCycleCountWindow() {
  openWindow('cycle-count', 'Cycle Count Execution', 'cycle-count-form')
}

function openBOMMasterWindow() {
  fetchBOMParents()
  openWindow('bom-master', 'Bill of Materials Master', 'bom-table')
}

// Fetch list of parent items that have BOMs
async function fetchBOMParents() {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    const response = await axios.get('http://localhost:8000/api/bom/parents', { headers })
    bomParentsData.value = response.data
    selectedBOMParent.value = null
    selectedBOMRevision.value = null
    bomDetailsData.value = []
  } catch (error) {
    console.error('Failed to fetch BOM parents:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to load BOM list'
    alert(errorMsg)
  }
}

// Fetch BOM locations for dropdown
async function fetchBOMLocations() {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    const response = await axios.get('http://localhost:8000/api/bom/locations/list', { headers })
    bomLocationsData.value = response.data
  } catch (error) {
    console.error('Failed to fetch locations:', error)
  }
}

// Search BOMs
async function searchBOMs() {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    const params = new URLSearchParams()
    if (bomSearchParent.value) params.append('parent_search', bomSearchParent.value)
    if (bomSearchChild.value) params.append('child_search', bomSearchChild.value)
    
    const response = await axios.get(`http://localhost:8000/api/bom/search?${params.toString()}`, { headers })
    
    // Group results by parent_item_id
    const grouped = {}
    response.data.forEach(bom => {
      if (!grouped[bom.parent_item_id]) {
        grouped[bom.parent_item_id] = {
          id: bom.parent_item_id,
          item_code: bom.parent_item_code,
          item_name: bom.parent_item_name,
          bom_type: bom.bom_type,
          revision: bom.revision,
          status: bom.status,
          component_count: 0
        }
      }
      grouped[bom.parent_item_id].component_count++
    })
    
    bomParentsData.value = Object.values(grouped)
  } catch (error) {
    console.error('Failed to search BOMs:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to search BOMs'
    alert(errorMsg)
  }
}

// Fetch BOM details for a specific parent and revision
async function fetchBOMDetails(parentItemId, revision = null) {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    let url = `http://localhost:8000/api/bom/parent/${parentItemId}`
    if (revision) url += `?revision=${revision}`
    
    const response = await axios.get(url, { headers })
    bomDetailsData.value = response.data
    selectedBOMParent.value = parentItemId
    if (response.data.length > 0) {
      selectedBOMRevision.value = response.data[0].revision
    }
  } catch (error) {
    console.error('Failed to fetch BOM details:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to load BOM details'
    alert(errorMsg)
  }
}

// Create new BOM revision
async function createNewRevision(parentItemId, sourceRevision = null) {
  if (!confirm(`Create new revision${sourceRevision ? ` (copy from Rev ${sourceRevision})` : ''}?`)) return
  
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    let url = `http://localhost:8000/api/bom/revision/new/${parentItemId}`
    if (sourceRevision) url += `?source_revision=${sourceRevision}`
    
    const response = await axios.post(url, {}, { headers })
    alert(response.data.message)
    await fetchBOMParents()
    await fetchBOMDetails(parentItemId)
  } catch (error) {
    console.error('Failed to create revision:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to create revision'
    alert(errorMsg)
  }
}

// Set BOM revision status
async function setRevisionStatus(parentItemId, revision, newStatus) {
  if (!confirm(`Set revision ${revision} to ${newStatus}?`)) return
  
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    await axios.patch(
      `http://localhost:8000/api/bom/revision/status/${parentItemId}/${revision}?new_status=${newStatus}`,
      {},
      { headers }
    )
    alert(`Revision ${revision} set to ${newStatus}`)
    await fetchBOMParents()
    await fetchBOMDetails(parentItemId, revision)
  } catch (error) {
    console.error('Failed to set revision status:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to set status'
    alert(errorMsg)
  }
}

// Export BOMs
async function exportBOMs(parentItemIds = [], includeAllRevisions = false) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/bom/export',
      {
        parent_item_ids: parentItemIds,
        include_all_revisions: includeAllRevisions,
        include_inactive: false
      },
      {
        headers: getAuthHeaders(),
        responseType: 'blob'
      }
    )
    
    // Download the file with local date
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bom_export_${formatDateLocal(new Date())}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export BOMs:', error)
    alert('Failed to export BOMs')
  }
}

// Open BOM form for adding new BOM
function openBOMForm(mode, parentId = null, bomLine = null) {
  bomFormMode.value = mode
  fetchBOMLocations()  // Load locations for dropdown
  
  if (mode === 'add') {
    bomFormData.value = {
      parent_item_id: parentId,
      child_item_id: null,
      bom_type: 'ASSEMBLY',
      is_template: true,
      sequence_order: bomDetailsData.value.length + 1,
      quantity: 1,
      percentage: null,
      is_optional: false,
      scrap_factor: 0,
      production_location_id: null,
      storage_location_id: null,
      is_byproduct: false,
      remark: '',
      revision: selectedBOMRevision.value || 1,
      status: 'ACTIVE',
      active_date: null,
      inactive_date: null,
      child_search: ''
    }
    editingBOMId.value = null
  } else if (mode === 'edit' && bomLine) {
    bomFormData.value = {
      parent_item_id: bomLine.parent_item_id,
      child_item_id: bomLine.child_item_id,
      bom_type: bomLine.bom_type,
      is_template: bomLine.is_template,
      sequence_order: bomLine.sequence_order,
      quantity: bomLine.quantity,
      percentage: bomLine.percentage,
      is_optional: bomLine.is_optional,
      scrap_factor: bomLine.scrap_factor || 0,
      production_location_id: bomLine.production_location_id,
      storage_location_id: bomLine.storage_location_id,
      is_byproduct: bomLine.is_byproduct,
      remark: bomLine.remark || '',
      revision: bomLine.revision,
      status: bomLine.status || 'ACTIVE',
      active_date: bomLine.active_date,
      inactive_date: bomLine.inactive_date,
      child_search: ''
    }
    editingBOMId.value = bomLine.id
  }
}

// Submit BOM form
async function handleBOMSubmit() {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    
    if (!bomFormData.value.parent_item_id) {
      alert('Please select a parent item (Finished Good/WIP)')
      return
    }
    if (!bomFormData.value.child_item_id) {
      alert('Please select a child item')
      return
    }
    if (!bomFormData.value.quantity || bomFormData.value.quantity <= 0) {
      alert('Quantity must be greater than 0')
      return
    }
    
    // Prepare data with all new fields
    const { child_search, ...payload } = bomFormData.value
    const submitData = {
      ...payload,
      revision: bomFormData.value.revision || selectedBOMRevision.value || 1
    }
    
    if (bomFormMode.value === 'add') {
      await axios.post('http://localhost:8000/api/bom/', submitData, { headers })
      alert('BOM line added successfully')
    } else {
      // Use BOMUpdate schema for updates (only send changed fields)
      const updateData = {
        bom_type: bomFormData.value.bom_type,
        is_template: bomFormData.value.is_template,
        sequence_order: bomFormData.value.sequence_order,
        quantity: bomFormData.value.quantity,
        percentage: bomFormData.value.percentage,
        is_optional: bomFormData.value.is_optional,
        scrap_factor: bomFormData.value.scrap_factor,
        production_location_id: bomFormData.value.production_location_id,
        storage_location_id: bomFormData.value.storage_location_id,
        is_byproduct: bomFormData.value.is_byproduct,
        remark: bomFormData.value.remark,
        status: bomFormData.value.status,
        active_date: bomFormData.value.active_date,
        inactive_date: bomFormData.value.inactive_date
      }
      await axios.put(`http://localhost:8000/api/bom/${editingBOMId.value}`, updateData, { headers })
      alert('BOM line updated successfully')
    }
    
    // Refresh data
    if (bomFormData.value.parent_item_id) {
      await fetchBOMDetails(bomFormData.value.parent_item_id, bomFormData.value.revision)
    }
    await fetchBOMParents()
    
    // Reset form
    resetBOMForm(true)
    return true
  } catch (error) {
    console.error('Failed to save BOM:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to save BOM'
    alert(errorMsg)
    return false
  }
}

// Delete BOM line
async function deleteBOMLine(bomId, parentItemId) {
  if (!confirm('Are you sure you want to delete this BOM line?')) return
  
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    await axios.delete(`http://localhost:8000/api/bom/${bomId}`, { headers })
    alert('BOM line deleted successfully')
    await fetchBOMDetails(parentItemId)
    await fetchBOMParents()
  } catch (error) {
    console.error('Failed to delete BOM line:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to delete BOM line'
    alert(errorMsg)
  }
}

// Delete entire BOM for a parent
async function deleteEntireBOM(parentItemId, revision = null) {
  const msg = revision 
    ? `Are you sure you want to delete revision ${revision} of this BOM?`
    : 'Are you sure you want to delete ALL revisions of this BOM?'
  if (!confirm(msg)) return
  
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    let url = `http://localhost:8000/api/bom/parent/${parentItemId}`
    if (revision) url += `?revision=${revision}`
    
    await axios.delete(url, { headers })
    alert('BOM deleted successfully')
    await fetchBOMParents()
    selectedBOMParent.value = null
    selectedBOMRevision.value = null
    bomDetailsData.value = []
  } catch (error) {
    console.error('Failed to delete BOM:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to delete BOM'
    alert(errorMsg)
  }
}

// Reset BOM form
function resetBOMForm(preserveParent = false) {
  const parentId = preserveParent ? selectedBOMParent.value : null
  const revision = preserveParent ? (selectedBOMRevision.value || 1) : 1
  bomFormData.value = {
    parent_item_id: parentId,
    child_item_id: null,
    bom_type: 'ASSEMBLY',
    is_template: true,
    sequence_order: 0,
    quantity: 1,
    percentage: null,
    is_optional: false,
    scrap_factor: 0,
    production_location_id: null,
    storage_location_id: null,
    is_byproduct: false,
    remark: '',
    revision,
    status: 'ACTIVE',
    active_date: null,
    inactive_date: null,
    child_search: ''
  }
  bomFormMode.value = 'add'
  editingBOMId.value = null
}

// Open new BOM creation (for a new parent item)
function openNewBOMWindow(windowId) {
  // Fetch items list and locations
  fetchInventory()
  fetchBOMLocations()
  resetBOMForm(false)
  openWindow('bom-new', 'Create New BOM', 'bom-form')
}

function openUserMasterWindow() {
  if (userRole.value !== 'admin') {
    alert('Access denied. Only administrators can access User Management.')
    return
  }
  fetchUsers()
  openWindow('user-master', 'User Management', 'users-table')
}

function openUserForm(mode, userData, parentWindowId) {
  const formData = mode === 'add' 
    ? { username: '', email: '', full_name: '', role: 'user', password: '', confirmPassword: '' }
    : { 
        id: userData.id,
        username: userData.username, 
        email: userData.email, 
        full_name: userData.full_name, 
        role: userData.role,
        theme_preference: userData.theme_preference || 'RETRO_EARTH',
        language: userData.language || 'en',
        is_active: userData.is_active
      }
  
  const title = mode === 'add' ? 'Create New User' : `Edit User: ${userData.username}`
  openWindow(`user-form-${Date.now()}`, title, 'user-form', { mode, formData, parentWindowId })
}

async function handleUserSubmit(formData, mode, windowId) {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }
    
    if (mode === 'add') {
      // Validate required fields
      if (!formData.username || !formData.email || !formData.full_name || !formData.password) {
        alert('Please fill in all required fields')
        return
      }
      if (formData.password !== formData.confirmPassword) {
        alert('Passwords do not match')
        return
      }
      if (formData.password.length < 6) {
        alert('Password must be at least 6 characters')
        return
      }
      
      await axios.post('http://localhost:8000/api/users', {
        username: formData.username,
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        password: formData.password
      }, { headers })
      
      alert('User created successfully!')
    } else {
      // Update user
      await axios.put(`http://localhost:8000/api/users/${formData.id}`, {
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        theme_preference: formData.theme_preference,
        language: formData.language,
        is_active: formData.is_active
      }, { headers })
      
      alert('User updated successfully!')
    }
    
    closeWindow(windowId)
    fetchUsers()
  } catch (error) {
    console.error('Failed to save user:', error)
    alert(parseApiError(error, 'User'))
  }
}

async function toggleUserStatus(user) {
  if (!confirm(`Are you sure you want to ${user.is_active ? 'deactivate' : 'activate'} user "${user.username}"?`)) {
    return
  }
  
  try {
    await axios.post(`http://localhost:8000/api/users/${user.id}/toggle-status`, {}, {
      headers: getAuthHeaders()
    })
    
    alert(`User ${user.is_active ? 'deactivated' : 'activated'} successfully!`)
    fetchUsers()
  } catch (error) {
    console.error('Failed to toggle user status:', error)
    alert(parseApiError(error, 'User'))
  }
}

async function handleResetPassword(user) {
  const newPassword = prompt(`Enter new password for user "${user.username}" (min 6 characters):`)
  
  if (!newPassword) return
  
  if (newPassword.length < 6) {
    alert('Password must be at least 6 characters')
    return
  }
  
  try {
    await axios.post(`http://localhost:8000/api/users/${user.id}/change-password`, {
      new_password: newPassword
    }, {
      headers: getAuthHeaders()
    })
    
    alert(`Password reset successfully for user "${user.username}"`)
  } catch (error) {
    console.error('Failed to reset password:', error)
    alert(parseApiError(error, 'User'))
  }
}

// Lifecycle
let timer
onMounted(async () => {
  timer = setInterval(() => currentTime.value = new Date(), 1000)
  // Check for existing token and restore user session
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const response = await axios.get('http://localhost:8000/api/auth/me', {
        headers: getAuthHeaders()
      })
      isLoggedIn.value = true
      if (response.data && response.data.role) {
        userRole.value = response.data.role
        console.log('App.vue: Restored user role from API:', userRole.value)
      }
    } catch (error) {
      console.error('Failed to restore user session:', error)
      // Token might be invalid, clear it
      localStorage.removeItem('token')
      isLoggedIn.value = false
    }
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
