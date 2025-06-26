// bytchat-panel/src/components/modals/CreateBotModal.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from 'lucide-react';

// 1. Definimos el schema de validación con Zod
const formSchema = z.object({
  name: z.string().min(1, { message: "El nombre no puede estar vacío." }).max(50, { message: "El nombre no puede tener más de 50 caracteres." }),
  description: z.string().max(200, { message: "La descripción no puede tener más de 200 caracteres." }).optional(),
  system_prompt: z.string().min(1, { message: "El prompt del sistema no puede estar vacío." }),
});

// Definimos el tipo para los datos del formulario que se pasarán
export type BotCreateData = z.infer<typeof formSchema>;

interface CreateBotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: BotCreateData) => void;
  isSubmitting: boolean;
}

const CreateBotModal = ({ isOpen, onClose, onSubmit, isSubmitting }: CreateBotModalProps) => {
  // 2. Configuramos el formulario con react-hook-form y zod
  const form = useForm<BotCreateData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
      system_prompt: "Eres un asistente de IA servicial.",
    },
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[480px] bg-white">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">Crear Nuevo Bot</DialogTitle>
          <DialogDescription>
            Dale una identidad y un propósito a tu nuevo asistente de IA.
          </DialogDescription>
        </DialogHeader>
        {/* 3. Estructura del formulario */}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nombre del Bot</FormLabel>
                  <FormControl>
                    <Input placeholder="Ej: Asistente de Ventas" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descripción (Opcional)</FormLabel>
                  <FormControl>
                    <Input placeholder="¿Cuál es el rol de este bot?" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="system_prompt"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Instrucción Principal (System Prompt)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Define el comportamiento principal de tu bot."
                      className="resize-none"
                      rows={4}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting}>
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creando...
                  </>
                ) : (
                  "Crear Bot"
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateBotModal;