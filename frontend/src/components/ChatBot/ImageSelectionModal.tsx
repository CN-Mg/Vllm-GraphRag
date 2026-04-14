import { Dialog, Button, Typography } from '@neo4j-ndl/react';
import { useState, useEffect } from 'react';
import { useCredentials } from '../../context/UserCredentials';
import { getImagesListAPI, ImageNode } from '../../services/QnaAPI';

interface ImageSelectionModalProps {
  open: boolean;
  onClose: () => void;
  onImageSelected: (imageUrl: string) => void;
  onSendMessage: (imageUrl: string, message: string) => void;
}

export default function ImageSelectionModal({
  open,
  onClose,
  onImageSelected,
  onSendMessage,
}: ImageSelectionModalProps) {
  const { userCredentials } = useCredentials();
  const [images, setImages] = useState<ImageNode[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageNode | null>(null);
  const [userMessage, setUserMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (open && userCredentials?.uri) {
      fetchImages();
    }
  }, [open, userCredentials]);

  const fetchImages = async () => {
    try {
      setLoading(true);
      const { response } = await getImagesListAPI(userCredentials);
      if (response.data?.status === 'Success') {
        setImages(response.data.data || []);
      }
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelect = (image: ImageNode) => {
    setSelectedImage(image);
    onImageSelected(image.img_url);
  };

  const handleSendMessage = () => {
    if (selectedImage && userMessage.trim()) {
      setSending(true);
      onSendMessage(selectedImage.img_url, userMessage.trim());
    }
  };

  const handleClose = () => {
    setSelectedImage(null);
    setUserMessage('');
    onClose();
  };

  return (
    <Dialog
      size="large"
      open={open}
      onClose={handleClose}
      aria-labelledby="image-selection-dialog"
    >
      <Dialog.Header id="image-selection-dialog">
        Image Analysis - Select an Image
      </Dialog.Header>
      <Dialog.Content>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <Typography variant="body-medium">
            Select an image from the list below to analyze with the Vision LLM.
            The associated chunks will provide additional context.
          </Typography>

          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '16px' }}>
              <Typography variant="body-medium">Loading images...</Typography>
            </div>
          ) : images.length === 0 ? (
            <Typography variant="body-medium" textAlign="center">
              No images found. Please process some documents with images first.
            </Typography>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div
                style={{
                  maxHeight: '350px',
                  overflowY: 'auto',
                  border: '1px solid #e0e0e',
                  borderRadius: '4px',
                  padding: '8px',
                }}
              >
                {images.map((image, index) => (
                  <div
                    key={index}
                    style={{
                      border: selectedImage?.img_url === image.img_url ? '2px solid #1976d2' : '1px solid #e0e0e',
                      borderRadius: '8px',
                      padding: '12px',
                      cursor: 'pointer',
                    }}
                    onClick={() => handleImageSelect(image)}
                  >
                    <Typography variant="body-small" fontWeight="bold">
                      Page {image.page_number} - Image {image.img_index}
                    </Typography>
                    <Typography variant="body-small" noWrap>
                      {image.img_url.split('/').pop()}
                    </Typography>
                    <Typography variant="body-small" style={{ color: '#6b7280' }}>
                      {image.chunks.length} chunk{image.chunks.length !== 1 ? 's' : ''}
                    </Typography>
                  </div>
                ))}
              </div>

              {/* Selected Image Info */}
              {selectedImage && (
                <div
                  style={{
                    marginTop: '16px',
                    padding: '16px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px',
                  }}
                >
                  <Typography variant="subheading-medium" fontWeight="bold">
                    Selected Image
                  </Typography>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <Typography variant="body-small">
                      <strong>URL:</strong> {selectedImage.img_url}
                    </Typography>
                    <Typography variant="body-small">
                      <strong>Document:</strong> {selectedImage.file_name}
                    </Typography>
                    <Typography variant="body-small">
                      <strong>Page:</strong> {selectedImage.page_number}
                    </Typography>
                  </div>
                </div>
              )}

              {/* Message Input */}
              {selectedImage && (
                <div style={{ marginTop: '16px' }}>
                  <Typography variant="body-medium" fontWeight="bold">
                    Your Question for Image Analysis
                  </Typography>
                  <div
                    style={{
                      padding: '12px',
                      border: '1px solid #e0e0e',
                      borderRadius: '4px',
                      backgroundColor: '#ffffff',
                    }}
                  >
                    <input
                      type="text"
                      placeholder="Ask about the selected image..."
                      value={userMessage}
                      onChange={(e) => setUserMessage(e.target.value)}
                      disabled={sending}
                      style={{
                        width: '100%',
                        border: 'none',
                        outline: 'none',
                        fontSize: '14px',
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '16px' }}>
            <Button onClick={handleClose} disabled={sending}>
              Cancel
            </Button>
            <Button
              onClick={handleSendMessage}
              disabled={!selectedImage || !userMessage.trim() || sending}
              intent="primary"
            >
              {sending ? 'Analyzing...' : 'Analyze Image'}
            </Button>
          </div>
        </div>
      </Dialog.Content>
    </Dialog>
  );
}
