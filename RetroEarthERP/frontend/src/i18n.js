/**
 * i18n Configuration for Multi-language Support
 * Supports: English (en) and Thai (th)
 */
import { createI18n } from 'vue-i18n'

const messages = {
    en: {
        common: {
            login: 'Login',
            logout: 'Logout',
            username: 'Username',
            password: 'Password',
            save: 'Save',
            cancel: 'Cancel',
            delete: 'Delete',
            edit: 'Edit',
            create: 'Create',
            search: 'Search',
            filter: 'Filter',
            loading: 'Loading...',
            error: 'Error',
            success: 'Success',
            confirm: 'Confirm',
            close: 'Close',
        },
        desktop: {
            inventory: 'Inventory',
            purchase: 'Purchase',
            sales: 'Sales',
            production: 'Production',
            mrp: 'MRP',
            settings: 'Settings',
            appMarket: 'App Market',
            master: 'Master Data',
        },
        auth: {
            welcomeBack: 'Welcome Back',
            loginPrompt: 'Please login to continue',
            invalidCredentials: 'Invalid username or password',
            loginSuccess: 'Login successful',
        },
        settings: {
            companyInfo: 'Company Information',
            license: 'License',
            theme: 'Theme',
            language: 'Language',
            users: 'Users',
            activateLicense: 'Activate License',
            currentPackage: 'Current Package',
        },
        themes: {
            retroEarth: 'Retro Earth',
            modernClean: 'Modern Clean',
            spaceFuture: 'Space Future',
        },
    },
    th: {
        common: {
            login: 'เข้าสู่ระบบ',
            logout: 'ออกจากระบบ',
            username: 'ชื่อผู้ใช้',
            password: 'รหัสผ่าน',
            save: 'บันทึก',
            cancel: 'ยกเลิก',
            delete: 'ลบ',
            edit: 'แก้ไข',
            create: 'สร้าง',
            search: 'ค้นหา',
            filter: 'กรอง',
            loading: 'กำลังโหลด...',
            error: 'ข้อผิดพลาด',
            success: 'สำเร็จ',
            confirm: 'ยืนยัน',
            close: 'ปิด',
        },
        desktop: {
            inventory: 'คลังสินค้า',
            purchase: 'จัดซื้อ',
            sales: 'ขาย',
            production: 'ผลิต',
            mrp: 'วางแผนวัตถุดิบ',
            settings: 'ตั้งค่า',
            appMarket: 'ร้านแอป',
            master: 'ข้อมูลหลัก',
        },
        auth: {
            welcomeBack: 'ยินดีต้อนรับกลับ',
            loginPrompt: 'กรุณาเข้าสู่ระบบเพื่อดำเนินการต่อ',
            invalidCredentials: 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง',
            loginSuccess: 'เข้าสู่ระบบสำเร็จ',
        },
        settings: {
            companyInfo: 'ข้อมูลบริษัท',
            license: 'ใบอนุญาต',
            theme: 'ธีม',
            language: 'ภาษา',
            users: 'ผู้ใช้',
            activateLicense: 'เปิดใช้งานใบอนุญาต',
            currentPackage: 'แพ็คเกจปัจจุบัน',
        },
        themes: {
            retroEarth: 'เรโทร เอิร์ธ',
            modernClean: 'โมเดิร์น คลีน',
            spaceFuture: 'สเปซ ฟิวเจอร์',
        },
    },
}

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
})

export default i18n
