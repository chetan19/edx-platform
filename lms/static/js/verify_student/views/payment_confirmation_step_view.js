/**
 * View for the "payment confirmation" step of the payment/verification flow.
 */
var edx = edx || {};

(function( $ ) {
    'use strict';

    edx.verify_student = edx.verify_student || {};

    // The "Verify Later" button goes directly to the dashboard,
    // The "Verify Now" button reloads this page with the "skip-first-step"
    // flag set.  This allows the user to navigate back to the confirmation
    // if he/she wants to.
    // For this reason, we don't need any custom click handlers here.
    edx.verify_student.PaymentConfirmationStepView = edx.verify_student.StepView.extend({
        postRender: function() {
            // Track clicks on "Verify Now" button
            $( "#verify_now_button" ).on( 'click', function() {
                window.analytics.track( 'edx.bi.user.verify.now', {
                    category: 'verification'
                });
            });

            // Track clicks on "Verify Later" button
            $( "#verify_later_button" ).on( 'click', function() {
                window.analytics.track( 'edx.bi.user.verify.later', {
                    category: 'verification'
                });
            });
        }
    });

})( jQuery );
