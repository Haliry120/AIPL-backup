class UserManager {  
    constructor() {  
        this.userId = localStorage.getItem('user_id') || this.generateUserId();  
        localStorage.setItem('user_id', this.userId);  
    }  
      
    generateUserId() {  
        return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;  
    }  
      
    getUserId() {  
        return this.userId;  
    }  
      
    setUserId(userId) {  
        this.userId = userId;  
        localStorage.setItem('user_id', userId);  
    }  
}  
  
export default new UserManager();