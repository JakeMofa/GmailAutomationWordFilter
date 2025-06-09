from labeler import GmailLabeler

if __name__ == '__main__':
    labeler = GmailLabeler()
    labeler.label_rejections()
    labeler.label_interviews()
