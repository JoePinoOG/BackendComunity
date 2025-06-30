import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonHeader,
  IonIcon,
  IonTitle,
  IonToolbar,
  IonDatetime,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonCardSubtitle,
  IonButton,
  IonButtons,
  IonBackButton,
  IonFab,
  IonFabButton,
  IonList,
  IonItem,
  IonLabel,
  IonBadge,
  IonSegment,
  IonSegmentButton,
  IonGrid,
  IonRow,
  IonCol,
  IonChip,
  IonAvatar,
  IonTextarea,
  IonInput,
  IonSelect,
  IonSelectOption,
  IonCheckbox,
  IonModal,
  IonRefresher,
  IonRefresherContent,
  AlertController,
  ToastController,
  ActionSheetController,
  ModalController
} from '@ionic/angular/standalone';
import { RouterLink } from '@angular/router';
import { addIcons } from 'ionicons';
import { 
  calendar, 
  add, 
  people, 
  document, 
  time,
  location,
  checkmark,
  close,
  create,
  trash,
  eye,
  pencil,
  send,
  refresh,
  filter,
  search,
  calendarOutline,
  listOutline,
  documentTextOutline
} from 'ionicons/icons';
import { ReunionesService } from '../services/reuniones.service';
import { AuthService, Usuario } from '../services/authservice.service';

// Interfaces actualizadas según el backend
export interface Reunion {
  id?: number;
  motivo: 'ORDINARIA' | 'EXTRAORDINARIA' | 'EMERGENCIA';
  fecha: string;
  lugar: string;
  descripcion: string;
  convocante?: number;
  creada_en?: string;
}

export interface Acta {
  id?: number;
  reunion?: number;
  contenido: string;
  estado: 'BORRADOR' | 'PENDIENTE' | 'VALIDADA';
  creado_por?: number;
  firmado_presidente?: boolean;
  firmado_secretario?: boolean;
  ultima_modificacion?: string;
}

@Component({
  selector: 'app-reuniones',
  templateUrl: './reuniones.page.html',
  styleUrls: ['./reuniones.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    IonContent,
    IonHeader,
    IonIcon,
    IonTitle,
    IonToolbar,
    IonDatetime,
    IonCard,
    IonCardContent,
    IonCardHeader,
    IonCardTitle,
    IonCardSubtitle,
    IonButton,
    IonButtons,
    IonBackButton,
    IonFab,
    IonFabButton,
    IonList,
    IonItem,
    IonLabel,
    IonBadge,
    IonSegment,
    IonSegmentButton,
    IonGrid,
    IonRow,
    IonCol,
    IonChip,
    IonAvatar,
    IonTextarea,
    IonInput,
    IonSelect,
    IonSelectOption,
    IonCheckbox,
    IonModal,
    IonRefresher,
    IonRefresherContent
  ]
})
export class ReunionesPage implements OnInit {
  @ViewChild(IonModal) modal!: IonModal;
  
  selectedTab = 'reuniones';
  reuniones: Reunion[] = [];
  actas: Acta[] = [];
  selectedDate: string = new Date().toISOString();
  userInfo: Usuario | null = null;
  
  // Modal states
  isModalOpen = false;
  modalType: 'reunion' | 'acta' | 'detalle' = 'reunion';
  selectedReunion: Reunion | null = null;
  selectedActa: Acta | null = null;
  
  // Form data - actualizado según backend
  nuevaReunion: Partial<Reunion> = {
    motivo: 'ORDINARIA',
    fecha: '',
    lugar: '',
    descripcion: ''
  };
  
  nuevaActa: Partial<Acta> = {
    contenido: '',
    estado: 'BORRADOR'
  };
  
  // Filters
  filtroMotivo: 'TODOS' | 'ORDINARIA' | 'EXTRAORDINARIA' | 'EMERGENCIA' = 'TODOS';
  filtroEstadoActa: 'TODOS' | 'BORRADOR' | 'PENDIENTE' | 'VALIDADA' = 'TODOS';
  
  constructor(
    private reunionesService: ReunionesService,
    private authService: AuthService,
    private alertController: AlertController,
    private toastController: ToastController,
    private actionSheetController: ActionSheetController,
    private modalController: ModalController
  ) {
    addIcons({refresh,time,location,eye,pencil,trash,calendarOutline,add,filter,checkmark,listOutline,documentTextOutline,close,document,calendar,people,create,send,search});
  }

  ngOnInit() {
    this.loadUserData();
    this.loadReuniones();
    this.loadActas();
  }
  
  loadUserData() {
    this.authService.getProfile().subscribe({
      next: (user) => {
        this.userInfo = user;
      },
      error: (err) => {
        console.error('Error al obtener perfil de usuario:', err);
      }
    });
  }
  
  async loadReuniones() {
    try {
      // URL corregida según el backend: /api/reuniones/reuniones/
      const response = await fetch('https://backendcomunity.onrender.com/api/reuniones/reuniones/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.authService.getToken()}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const reuniones = await response.json();
        console.log('Reuniones obtenidas:', reuniones);
        
        if (Array.isArray(reuniones)) {
          this.reuniones = reuniones;
        } else {
          console.warn('Las reuniones no son un array:', reuniones);
          this.reuniones = [];
        }
      } else {
        console.error('Error en respuesta:', response.status, response.statusText);
        this.presentToast(`Error al cargar reuniones: ${response.status}`, 'danger');
        this.reuniones = [];
      }
    } catch (error: any) {
      console.error('Error cargando reuniones:', error);
      this.reuniones = [];
      this.presentToast('Error de conexión al cargar reuniones', 'danger');
    }
  }
  
  async loadActas() {
    try {
      // URL corregida según el backend: /api/reuniones/actas/
      const response = await fetch('https://backendcomunity.onrender.com/api/reuniones/actas/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.authService.getToken()}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const actas = await response.json();
        console.log('Actas obtenidas:', actas);
        
        if (Array.isArray(actas)) {
          this.actas = actas;
        } else {
          console.warn('Las actas no son un array:', actas);
          this.actas = [];
        }
      } else {
        console.error('Error en respuesta actas:', response.status);
        this.actas = [];
      }
    } catch (error: any) {
      console.error('Error cargando actas:', error);
      this.actas = [];
    }
  }
  
  // Permissions - simplificados
  canCreateReunion(): boolean {
    return this.userInfo != null; // Todos los usuarios autenticados pueden crear
  }
  
  canEditReunion(reunion: Reunion): boolean {
    return this.userInfo != null; // Simplificado
  }
  
  canDeleteReunion(reunion: Reunion): boolean {
    return this.userInfo != null; // Simplificado
  }
  
  canCreateActa(): boolean {
    return this.userInfo != null;
  }
  
  canViewActas(): boolean {
    return true;
  }
  
  canEditActa(acta: Acta): boolean {
    return this.userInfo != null && acta.estado === 'BORRADOR';
  }

  // UI Actions
  onDateChange(event: any) {
    this.selectedDate = event.detail.value;
  }
  
  segmentChanged(event: any) {
    this.selectedTab = event.detail.value;
  }
  
  openModal(type: 'reunion' | 'acta' | 'detalle', item?: any) {
    this.modalType = type;
    if (type === 'detalle') {
      this.selectedReunion = item;
    } else if (type === 'acta') {
      this.selectedActa = item;
      this.nuevaActa.reunion = item?.id;
    }
    this.isModalOpen = true;
  }
  
  closeModal() {
    this.isModalOpen = false;
    this.resetForms();
  }
  
  resetForms() {
    this.nuevaReunion = {
      motivo: 'ORDINARIA',
      fecha: '',
      lugar: '',
      descripcion: ''
    };
    this.nuevaActa = {
      contenido: '',
      estado: 'BORRADOR'
    };
    this.selectedReunion = null;
    this.selectedActa = null;
  }
  
  async crearReunion() {
    // Validar campos requeridos según el backend
    if (!this.nuevaReunion.fecha || !this.nuevaReunion.lugar) {
      this.presentToast('Por favor completa fecha y lugar (campos requeridos)', 'warning');
      return;
    }
    
    try {
      // Preparar datos exactamente como espera el backend
      const reunion = {
        motivo: this.nuevaReunion.motivo || 'ORDINARIA',
        fecha: new Date(this.nuevaReunion.fecha!).toISOString(),
        lugar: this.nuevaReunion.lugar!,
        descripcion: this.nuevaReunion.descripcion || ''
      };
      
      console.log('Enviando reunión:', reunion);
      
      // Usar la URL correcta: /api/reuniones/reuniones/
      const response = await fetch('https://backendcomunity.onrender.com/api/reuniones/reuniones/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.authService.getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reunion)
      });

      if (response.ok) {
        const nuevaReunion = await response.json();
        console.log('Reunión creada:', nuevaReunion);
        this.presentToast('Reunión creada exitosamente', 'success');
        this.loadReuniones();
        this.closeModal();
      } else {
        const errorText = await response.text();
        console.error('Error del servidor:', response.status, errorText);
        this.presentToast(`Error ${response.status}: ${errorText}`, 'danger');
      }
    } catch (error: any) {
      console.error('Error creando reunión:', error);
      this.presentToast('Error de conexión al crear reunión', 'danger');
    }
  }
  
  async crearActa() {
    if (!this.nuevaActa.contenido) {
      this.presentToast('El contenido del acta es requerido', 'warning');
      return;
    }
    
    try {
      const acta = {
        reunion: this.nuevaActa.reunion,
        contenido: this.nuevaActa.contenido,
        estado: 'BORRADOR'
      };
      
      const response = await fetch('https://backendcomunity.onrender.com/api/reuniones/actas/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.authService.getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(acta)
      });

      if (response.ok) {
        this.presentToast('Acta creada exitosamente', 'success');
        this.loadActas();
        this.closeModal();
      } else {
        const errorText = await response.text();
        this.presentToast(`Error al crear acta: ${errorText}`, 'danger');
      }
    } catch (error) {
      this.presentToast('Error de conexión al crear acta', 'danger');
    }
  }
  
  async eliminarReunion(reunion: Reunion) {
    const alert = await this.alertController.create({
      header: 'Confirmar eliminación',
      message: '¿Está seguro de que desea eliminar esta reunión?',
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        {
          text: 'Eliminar',
          cssClass: 'danger',
          handler: async () => {
            try {
              const response = await fetch(`https://backendcomunity.onrender.com/api/reuniones/reuniones/${reunion.id}/`, {
                method: 'DELETE',
                headers: {
                  'Authorization': `Bearer ${this.authService.getToken()}`,
                }
              });

              if (response.ok) {
                this.presentToast('Reunión eliminada exitosamente', 'success');
                this.loadReuniones();
              } else {
                this.presentToast('Error al eliminar la reunión', 'danger');
              }
            } catch (error) {
              this.presentToast('Error de conexión al eliminar reunión', 'danger');
            }
          }
        }
      ]
    });
    await alert.present();
  }
  
  async presentToast(message: string, color: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color,
      position: 'bottom'
    });
    toast.present();
  }
  
  // Filters
  get reunionesFiltradas() {
    if (!Array.isArray(this.reuniones)) {
      return [];
    }
    return this.reuniones.filter(reunion => {
      const motivoMatch = this.filtroMotivo === 'TODOS' || reunion.motivo === this.filtroMotivo;
      return motivoMatch;
    });
  }
  
  get actasFiltradas() {
    if (!Array.isArray(this.actas)) {
      return [];
    }
    return this.actas.filter(acta => {
      const estadoMatch = this.filtroEstadoActa === 'TODOS' || acta.estado === this.filtroEstadoActa;
      return estadoMatch;
    });
  }
  
  // Utilities
  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  getMotivoColor(motivo: string): string {
    switch(motivo) {
      case 'ORDINARIA': return 'primary';
      case 'EXTRAORDINARIA': return 'warning';
      case 'EMERGENCIA': return 'danger';
      default: return 'medium';
    }
  }
  
  getEstadoActaColor(estado: string): string {
    switch(estado) {
      case 'BORRADOR': return 'medium';
      case 'PENDIENTE': return 'warning';
      case 'VALIDADA': return 'success';
      default: return 'medium';
    }
  }
  
  doRefresh(event: any) {
    Promise.all([this.loadReuniones(), this.loadActas()]).then(() => {
      event.target.complete();
    });
  }
}
