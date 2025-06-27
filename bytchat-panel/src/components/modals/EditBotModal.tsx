// bytchat-panel/src/components/modals/EditBotModal.tsx
import { useEffect } from 'react';
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
import { Bot } from '@/types';

const formSchema = z.object({
  name: z.string().min(1, { message: "El nombre no puede estar vacío." }).max(50),
  description: z.string().max(200).optional(),
  system_prompt: z.string().min(1, { message: "El prompt del sistema no puede estar vacío." }),
});

export type BotUpdateData = z.infer<typeof formSchema>;

interface EditBotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: BotUpdateData) => void;
  isSubmitting: boolean;
  bot: Bot | null; // El bot a editar
}

const EditBotModal = ({ isOpen, onClose, onSubmit, isSubmitting, bot }: EditBotModalProps) => {
  const form = useForm<BotUpdateData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: bot?.name || '',
      description: bot?.description || '',
      system_prompt: bot?.system_prompt || '',
    },
  });

  // Efecto para resetear el formulario con los datos del bot cuando cambie
  useEffect(() => {
    if (bot) {
      form.reset({
        name: bot.name,
        description: bot.description || '',
        system_prompt: bot.system_prompt || '',
      });
    }
  }, [bot, form]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[480px] bg-white">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">Editar Bot</DialogTitle>
          <DialogDescription>
            Ajusta los detalles de tu asistente.
          </DialogDescription>
        </DialogHeader>
        {bot && (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nombre del Bot</FormLabel>
                    <FormControl>
                      <Input {...field} />
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
                      <Input {...field} />
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
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Guardando...</>
                  ) : (
                    "Guardar Cambios"
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default EditBotModal;